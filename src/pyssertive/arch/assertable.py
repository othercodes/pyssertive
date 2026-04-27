import difflib
import fnmatch
import sys
from collections import deque
from collections.abc import Callable

import grimp

from pyssertive.arch.graph import build_graph

_STDLIB_TOKEN = "stdlib"
_GLOB_CHARS = "*?["

__all__ = ["AssertableArch"]


def _is_glob_pattern(s: str) -> bool:
    return any(c in s for c in _GLOB_CHARS)


class AssertableArch:
    """
    Fluent architecture assertions over a single module's import graph.

    Created via :func:`pyssertive.arch.assert_arch`. Each method either
    returns ``self`` (for chaining) or raises ``AssertionError`` with a
    message that lists every offending dependency.

    Three assertion families:

    * ``should_depend_on`` — reachability check; the source must import
      the target directly or transitively (``directly=True`` to require
      a direct edge).
    * ``should_not_depend_on`` — forbidden-import check; the source
      must not import the target by any path (``directly=True`` to
      ignore transitive paths).
    * ``should_only_depend_on`` — allow-list check; every dependency
      of the source must match an entry in the list. Direct imports
      by default; pass ``directly=False`` for transitive purity rules.
      The literal ``"stdlib"`` is a magic token expanding to any
      Python standard library top-level module.

    ``ignoring(patterns)`` accepts ``fnmatch`` glob patterns used to
    grandfather known violations. Patterns apply to chain traversals
    (the chain BFS skips matching modules so an alternate non-ignored
    path is still detected) and to the violation list of
    ``should_only_depend_on`` (matching dependencies are filtered out).

    Source and target modules are validated against the import graph;
    typos and unsupported external submodule paths raise ``ValueError``
    with a "Did you mean ...?" hint when a close match exists.
    """

    def __init__(self, module: str) -> None:
        self._module = module
        self._package = module.split(".")[0]
        graph = build_graph(self._package)
        if module not in graph.modules:
            raise ValueError(
                f"Source module {module!r} is not in the import graph for "
                f"package {self._package!r}.{_did_you_mean(module, graph)}"
            )
        self._ignored: list[str] = []

    def ignoring(self, patterns: str | list[str]) -> "AssertableArch":
        """Add ``fnmatch`` glob patterns excluded from chain checks and dependency lists."""
        new_patterns = [patterns] if isinstance(patterns, str) else list(patterns)
        self._ignored.extend(new_patterns)
        return self

    def module(
        self,
        name: str,
        callback: Callable[["AssertableArch | _MultiAssertableArch"], object] | None = None,
    ) -> "AssertableArch | _MultiAssertableArch":
        """
        Scope into a submodule, returning an assertable bound to it.

        ``name`` is resolved relative to the current scope unless it
        already starts with the parent path. Glob patterns are
        expanded against the graph. With a ``callback`` the nested
        assertable is passed to it and the outer scope is returned
        for continued chaining; without one the nested assertable is
        returned directly.
        """
        resolved = self._resolve_submodule(name)
        nested: AssertableArch | _MultiAssertableArch
        if _is_glob_pattern(resolved):
            nested = _MultiAssertableArch(_expand_glob_source(resolved))
        else:
            nested = AssertableArch(resolved)
        if callback is not None:
            callback(nested)
            return self
        return nested

    def _resolve_submodule(self, name: str) -> str:
        if name == self._module or name.startswith(f"{self._module}."):
            return name
        return f"{self._module}.{name}"

    def should_depend_on(
        self, target: str | list[str], directly: bool = False
    ) -> "AssertableArch":
        """
        Assert the source imports each ``target`` directly or transitively.

        ``directly=True`` requires a direct import edge — useful when
        the source must own the import explicitly rather than picking
        it up via a re-export.
        """
        targets = [target] if isinstance(target, str) else list(target)
        graph = build_graph(self._package)
        targets = self._expand_targets(targets, graph)
        for candidate in targets:
            self._validate_target(candidate, graph)
        missing: list[str] = []
        for candidate in targets:
            if directly:
                if candidate not in graph.find_modules_directly_imported_by(self._module):
                    missing.append(candidate)
            else:
                if self._find_chain(graph, candidate) is None:
                    missing.append(candidate)
        if missing:
            self._raise_violations("should depend on", missing)
        return self

    def should_not_depend_on(
        self, target: str | list[str], directly: bool = False
    ) -> "AssertableArch":
        """
        Assert the source does not import any ``target``, direct or transitive.

        ``directly=True`` only forbids direct imports; transitive
        paths through other modules are tolerated. Useful when the
        rule is "you must not write the import yourself" but reaching
        the target via an intermediate is acceptable.
        """
        targets = [target] if isinstance(target, str) else list(target)
        graph = build_graph(self._package)
        targets = self._expand_targets(targets, graph)
        for candidate in targets:
            self._validate_target(candidate, graph)
        violations: list[str] = []
        for candidate in targets:
            if directly:
                if candidate in graph.find_modules_directly_imported_by(self._module):
                    violations.append(f"{candidate} (direct import)")
            else:
                chain = self._find_chain(graph, candidate)
                if chain is not None:
                    violations.append(f"{candidate}: " + " → ".join(chain))
        if violations:
            self._raise_violations("should not depend on", violations)
        return self

    def should_only_depend_on(
        self, allowed: str | list[str], directly: bool = True
    ) -> "AssertableArch":
        """
        Assert every dependency of the source matches an entry in ``allowed``.

        Direct imports by default — what the module's source code
        actually uses. ``directly=False`` extends the check to the
        transitive closure for stricter purity rules (e.g. domain
        code must not transitively reach Django through any helper).
        """
        allowed_list = [allowed] if isinstance(allowed, str) else list(allowed)
        graph = build_graph(self._package)
        if directly:
            deps = graph.find_modules_directly_imported_by(self._module)
        else:
            deps = self._upstream_respecting_ignoring(graph)
        stdlib_allowed = _STDLIB_TOKEN in allowed_list
        explicit = [a for a in allowed_list if a != _STDLIB_TOKEN]
        violations = sorted(
            dep
            for dep in deps
            if not self._is_ignored(dep)
            and not (stdlib_allowed and dep.split(".")[0] in sys.stdlib_module_names)
            and not any(dep == a or dep.startswith(f"{a}.") for a in explicit)
        )
        if violations:
            self._raise_violations(
                f"should only depend on [{', '.join(allowed_list)}] but imports",
                violations,
            )
        return self

    def _expand_targets(self, targets: list[str], graph: grimp.ImportGraph) -> list[str]:
        expanded: list[str] = []
        for t in targets:
            if _is_glob_pattern(t):
                matches = sorted(m for m in graph.modules if fnmatch.fnmatch(m, t))
                if not matches:
                    raise ValueError(
                        f"Pattern {t!r} did not match any module in the import graph "
                        f"for package {self._package!r}."
                    )
                expanded.extend(matches)
            else:
                expanded.append(t)
        return expanded

    def _validate_target(self, target: str, graph: grimp.ImportGraph) -> None:
        if target in graph.modules:
            return
        top = target.split(".")[0]
        if top in graph.modules and top != self._package:
            raise ValueError(
                f"Target {target!r} is not a node in the graph. External "
                f"submodules are tracked at the top-level only — use "
                f"{top!r} instead."
            )
        raise ValueError(
            f"Target {target!r} is not in the import graph for "
            f"package {self._package!r}.{_did_you_mean(target, graph)}"
        )

    def _raise_violations(self, action: str, items: list[str]) -> None:
        raise AssertionError(
            f"{self._module} {action}:\n  - " + "\n  - ".join(items)
        )

    def _is_ignored(self, module: str) -> bool:
        return any(fnmatch.fnmatch(module, pattern) for pattern in self._ignored)

    def _upstream_respecting_ignoring(self, graph: grimp.ImportGraph) -> set[str]:
        if not self._ignored:
            return set(graph.find_upstream_modules(self._module))
        if self._is_ignored(self._module):
            return set()
        visited: set[str] = {self._module}
        queue: deque[str] = deque([self._module])
        upstream: set[str] = set()
        while queue:
            current = queue.popleft()
            for next_mod in graph.find_modules_directly_imported_by(current):
                if next_mod in visited or self._is_ignored(next_mod):
                    continue
                visited.add(next_mod)
                upstream.add(next_mod)
                queue.append(next_mod)
        return upstream

    def _find_chain(self, graph: grimp.ImportGraph, target: str) -> tuple[str, ...] | None:
        if not self._ignored:
            return graph.find_shortest_chain(self._module, target)
        if self._is_ignored(self._module):
            return None
        visited = {self._module}
        queue: deque[tuple[str, tuple[str, ...]]] = deque(
            [(self._module, (self._module,))]
        )
        while queue:
            current, path = queue.popleft()
            for next_mod in graph.find_modules_directly_imported_by(current):
                if next_mod in visited or self._is_ignored(next_mod):
                    continue
                new_path = (*path, next_mod)
                if next_mod == target:
                    return new_path
                visited.add(next_mod)
                queue.append((next_mod, new_path))
        return None


def _did_you_mean(name: str, graph: grimp.ImportGraph) -> str:
    matches = difflib.get_close_matches(name, list(graph.modules), n=1, cutoff=0.7)
    if matches:
        return f" Did you mean {matches[0]!r}?"
    return ""


class _MultiAssertableArch:
    """
    Wraps several :class:`AssertableArch` instances obtained by glob-expanding
    a source pattern. Each public method dispatches to every member and
    aggregates any AssertionErrors into a single message so callers see every
    failing source at once.
    """

    def __init__(self, sources: list[str]) -> None:
        self._members = [AssertableArch(s) for s in sources]

    def ignoring(self, patterns: str | list[str]) -> "_MultiAssertableArch":
        for member in self._members:
            member.ignoring(patterns)
        return self

    def should_depend_on(
        self, target: str | list[str], directly: bool = False
    ) -> "_MultiAssertableArch":
        return self._dispatch_assertion("should_depend_on", target, directly=directly)

    def should_not_depend_on(
        self, target: str | list[str], directly: bool = False
    ) -> "_MultiAssertableArch":
        return self._dispatch_assertion("should_not_depend_on", target, directly=directly)

    def should_only_depend_on(
        self, allowed: str | list[str], directly: bool = True
    ) -> "_MultiAssertableArch":
        return self._dispatch_assertion("should_only_depend_on", allowed, directly=directly)

    def module(
        self,
        name: str,
        callback: Callable[["AssertableArch | _MultiAssertableArch"], object] | None = None,
    ) -> "AssertableArch | _MultiAssertableArch":
        """Descend each member into ``name``, returning a flattened multi or invoking the callback."""
        nested_members: list[AssertableArch] = []
        for member in self._members:
            nested = member.module(name)
            if isinstance(nested, _MultiAssertableArch):
                nested_members.extend(nested._members)
            else:
                nested_members.append(nested)
        nested_multi = _MultiAssertableArch.__new__(_MultiAssertableArch)
        nested_multi._members = nested_members
        if callback is not None:
            callback(nested_multi)
            return self
        return nested_multi

    def _dispatch_assertion(self, method_name: str, *args: object, **kwargs: object) -> "_MultiAssertableArch":
        errors: list[str] = []
        for member in self._members:
            try:
                getattr(member, method_name)(*args, **kwargs)
            except AssertionError as exc:
                errors.append(str(exc))
        if errors:
            raise AssertionError("\n\n".join(errors))
        return self


def _expand_glob_source(pattern: str) -> list[str]:
    top = pattern.split(".")[0]
    if _is_glob_pattern(top):
        raise ValueError(
            f"Glob pattern {pattern!r} must have a fixed top-level package name."
        )
    graph = build_graph(top)
    matches = sorted(m for m in graph.modules if fnmatch.fnmatch(m, pattern))
    if not matches:
        raise ValueError(
            f"Pattern {pattern!r} did not match any module in package {top!r}."
        )
    return matches
