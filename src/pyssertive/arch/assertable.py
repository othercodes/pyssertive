import difflib
import fnmatch
import functools
import sys
from collections.abc import Callable

import grimp

from pyssertive.arch._chains import find_chain, find_package_chain, find_upstream, is_ignored


@functools.cache
def build_graph(package: str) -> grimp.ImportGraph:
    try:
        return grimp.build_graph(package, include_external_packages=True)
    except ValueError as exc:
        # grimp raises ValueError when the package cannot be located on
        # sys.path. Translate that to the stdlib ModuleNotFoundError so
        # callers see a familiar exception type. Other ValueErrors are
        # re-raised so unrelated grimp failures aren't masked.
        if "Could not find package" not in str(exc):
            raise
        raise ModuleNotFoundError(str(exc)) from exc


_STDLIB_TOKEN = "stdlib"
# fnmatch metacharacters — presence of any of these triggers glob expansion
# against the import graph rather than literal-string matching.
_GLOB_CHARS = "*?["

__all__ = [
    "AssertableArch",
    "AssertableLayers",
    "AssertableModules",
    "AssertableMultiArch",
    "assert_arch",
]


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
        """
        Add ``fnmatch`` glob patterns excluded from chain checks and dependency lists.

        Patterns accumulate across successive calls on the same assertable.
        Each ``assert_arch(...)`` invocation starts with an empty ignore list,
        so scoping is per-assertion-chain — there is no shared state between
        tests. Use a fresh ``assert_arch(...)`` to start over.
        """
        new_patterns = [patterns] if isinstance(patterns, str) else list(patterns)
        self._ignored.extend(new_patterns)
        return self

    def module(
        self,
        name: str,
        callback: Callable[["AssertableArch | AssertableMultiArch"], object] | None = None,
    ) -> "AssertableArch | AssertableMultiArch":
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
        nested: AssertableArch | AssertableMultiArch
        if _is_glob_pattern(resolved):
            nested = AssertableMultiArch(_expand_glob_source(resolved))
            for member in nested._members:
                member._ignored = list(self._ignored)
        else:
            nested = AssertableArch(resolved)
            nested._ignored = list(self._ignored)
        if callback is not None:
            callback(nested)
            return self
        return nested

    def _resolve_submodule(self, name: str) -> str:
        if name == self._module or name.startswith(f"{self._module}."):
            return name
        if self._module.startswith(f"{name}."):
            raise ValueError(
                f"module({name!r}) attempts to ascend from {self._module!r}; "
                "module() can only descend into the current scope."
            )
        return f"{self._module}.{name}"

    def should_depend_on(self, target: str | list[str], directly: bool = False) -> "AssertableArch":
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
        direct_deps = graph.find_modules_directly_imported_by(self._module) if directly else None
        missing: list[str] = []
        for candidate in targets:
            if direct_deps is not None:
                if candidate not in direct_deps:
                    missing.append(candidate)
            else:
                if find_chain(graph, self._module, candidate, self._ignored) is None:
                    missing.append(candidate)
        if missing:
            self._raise_violations("should depend on", missing)
        return self

    def should_not_depend_on(self, target: str | list[str], directly: bool = False) -> "AssertableArch":
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
        direct_deps = graph.find_modules_directly_imported_by(self._module) if directly else None
        violations: list[str] = []
        for candidate in targets:
            if direct_deps is not None:
                if candidate in direct_deps:
                    violations.append(f"{candidate} (direct import)")
            else:
                chain = find_chain(graph, self._module, candidate, self._ignored)
                if chain is not None:
                    violations.append(f"{candidate}: " + " → ".join(chain))
        if violations:
            self._raise_violations("should not depend on", violations)
        return self

    def should_only_depend_on(self, allowed: str | list[str], directly: bool = True) -> "AssertableArch":
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
            deps = find_upstream(graph, self._module, self._ignored)
        stdlib_allowed = _STDLIB_TOKEN in allowed_list
        explicit = [a for a in allowed_list if a != _STDLIB_TOKEN]
        violations = sorted(
            dep
            for dep in deps
            if not is_ignored(dep, self._ignored)
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
                        f"Pattern {t!r} did not match any module in the import graph for package {self._package!r}."
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
            f"Target {target!r} is not in the import graph for package {self._package!r}.{_did_you_mean(target, graph)}"
        )

    def _raise_violations(self, action: str, items: list[str]) -> None:
        raise AssertionError(f"{self._module} {action}:\n  - " + "\n  - ".join(items))


def _did_you_mean(name: str, graph: grimp.ImportGraph) -> str:
    matches = difflib.get_close_matches(name, list(graph.modules), n=1, cutoff=0.7)
    if matches:
        return f" Did you mean {matches[0]!r}?"
    return ""


class AssertableMultiArch:
    """
    Wraps several :class:`AssertableArch` instances obtained by glob-expanding
    a source pattern. Each public method dispatches to every member and
    aggregates any AssertionErrors into a single message so callers see every
    failing source at once.
    """

    def __init__(self, sources: list[str]) -> None:
        self._members = [AssertableArch(s) for s in sources]

    def ignoring(self, patterns: str | list[str]) -> "AssertableMultiArch":
        for member in self._members:
            member.ignoring(patterns)
        return self

    def should_depend_on(self, target: str | list[str], directly: bool = False) -> "AssertableMultiArch":
        return self._dispatch_assertion("should_depend_on", target, directly=directly)

    def should_not_depend_on(self, target: str | list[str], directly: bool = False) -> "AssertableMultiArch":
        return self._dispatch_assertion("should_not_depend_on", target, directly=directly)

    def should_only_depend_on(self, allowed: str | list[str], directly: bool = True) -> "AssertableMultiArch":
        return self._dispatch_assertion("should_only_depend_on", allowed, directly=directly)

    def module(
        self,
        name: str,
        callback: Callable[["AssertableArch | AssertableMultiArch"], object] | None = None,
    ) -> "AssertableArch | AssertableMultiArch":
        """Descend each member into ``name``, returning a flattened multi or invoking the callback."""
        nested_members: list[AssertableArch] = []
        for member in self._members:
            nested = member.module(name)
            if isinstance(nested, AssertableMultiArch):
                nested_members.extend(nested._members)
            else:
                nested_members.append(nested)
        nested_multi = AssertableMultiArch.__new__(AssertableMultiArch)
        nested_multi._members = nested_members
        if callback is not None:
            callback(nested_multi)
            return self
        return nested_multi

    def _dispatch_assertion(self, method_name: str, *args: object, **kwargs: object) -> "AssertableMultiArch":
        # Relies on AssertableArch._raise_violations prefixing each error with
        # the failing source module — concatenating str(exc) yields a self-
        # describing aggregated message. Changing that prefix elsewhere will
        # require labelling here.
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
        raise ValueError(f"Glob pattern {pattern!r} must have a fixed top-level package name.")
    graph = build_graph(top)
    matches = sorted(m for m in graph.modules if fnmatch.fnmatch(m, pattern))
    if not matches:
        raise ValueError(f"Pattern {pattern!r} did not match any module in package {top!r}.")
    return matches


class AssertableLayers:
    """
    Fluent layered-architecture assertion.

    Constructed via ``assert_arch.layers``. Each entry is a package or
    single-file module treated as a layer, ordered from lowest
    (foundational, no dependencies on layers above) to highest. The
    ``should_be_independent`` check enforces that no layer imports any
    layer that follows it in the list, direct or transitive.

    ``ignoring(patterns)`` accepts ``fnmatch`` glob patterns that are
    skipped during chain traversal so legacy violations can be
    grandfathered. An alternate non-ignored path still triggers the
    assertion, matching the semantic used elsewhere in the package.
    """

    def __init__(self, layers: list[str]) -> None:
        if len(layers) < 2:
            raise ValueError("assert_arch.layers requires at least two layers.")
        self._layers = list(layers)
        self._package = layers[0].split(".")[0]
        graph = build_graph(self._package)
        for layer in self._layers:
            if layer not in graph.modules:
                raise ValueError(f"Layer {layer!r} is not in the import graph for package {self._package!r}.")
        self._ignored: list[str] = []

    def ignoring(self, patterns: str | list[str]) -> "AssertableLayers":
        """
        Add fnmatch glob patterns excluded from chain traversal.

        Patterns accumulate; the list is per-instance, not global.
        """
        new_patterns = [patterns] if isinstance(patterns, str) else list(patterns)
        self._ignored.extend(new_patterns)
        return self

    def should_be_independent(self) -> "AssertableLayers":
        """Assert each layer only depends on layers preceding it in the list."""
        graph = build_graph(self._package)
        violations: list[str] = []
        for i, lower in enumerate(self._layers):
            for higher in self._layers[i + 1 :]:
                chain = find_package_chain(graph, lower, higher, self._ignored)
                if chain is not None:
                    violations.append(f"{lower} → {higher}: " + " → ".join(chain))
        if violations:
            raise AssertionError(
                "Layered architecture violations (each layer must depend "
                "only on prior layers):\n  - " + "\n  - ".join(violations)
            )
        return self


class AssertableModules:
    """
    Fluent isolation assertion across an unordered set of modules.

    Constructed via ``assert_arch.modules``. Each entry is a package
    or module that should not depend on any of the others, in either
    direction. ``should_be_isolated`` flags any cross-import; pair
    ``ignoring(patterns)`` with it to grandfather permitted bridges
    such as published events modules.
    """

    def __init__(self, modules: list[str]) -> None:
        if len(modules) < 2:
            raise ValueError("assert_arch.modules requires at least two modules.")
        self._modules = list(modules)
        self._package = modules[0].split(".")[0]
        graph = build_graph(self._package)
        for module in self._modules:
            if module not in graph.modules:
                raise ValueError(f"Module {module!r} is not in the import graph for package {self._package!r}.")
        self._ignored: list[str] = []

    def ignoring(self, patterns: str | list[str]) -> "AssertableModules":
        """
        Add fnmatch glob patterns excluded from cross-import detection.

        Patterns accumulate; the list is per-instance, not global.
        """
        new_patterns = [patterns] if isinstance(patterns, str) else list(patterns)
        self._ignored.extend(new_patterns)
        return self

    def should_be_isolated(self) -> "AssertableModules":
        """Assert no module in the set imports any other, direct or transitive."""
        graph = build_graph(self._package)
        violations: list[str] = []
        for src in self._modules:
            for dst in self._modules:
                if src == dst:
                    continue
                chain = find_package_chain(graph, src, dst, self._ignored)
                if chain is not None:
                    violations.append(f"{src} → {dst}: " + " → ".join(chain))
        if violations:
            raise AssertionError("Modules are not isolated:\n  - " + "\n  - ".join(violations))
        return self


class _AssertArch:
    """
    Callable entrypoint to architecture assertions.

    Invoke with a module path to obtain an :class:`AssertableArch`;
    call :meth:`layers` to obtain an :class:`AssertableLayers` for
    layered architecture rules.
    """

    def __call__(
        self,
        module: str,
        callback: Callable[[AssertableArch | AssertableMultiArch], object] | None = None,
    ) -> AssertableArch | AssertableMultiArch:
        """
        Return an assertable bound to ``module``. Glob patterns expand
        across the import graph. When ``callback`` is given it is
        invoked with the assertable so callers can scope a block of
        assertions inline.
        """
        arch: AssertableArch | AssertableMultiArch = (
            AssertableMultiArch(_expand_glob_source(module)) if _is_glob_pattern(module) else AssertableArch(module)
        )
        if callback is not None:
            callback(arch)
        return arch

    def layers(
        self,
        layers: list[str],
        callback: Callable[[AssertableLayers], object] | None = None,
    ) -> AssertableLayers:
        """Return an :class:`AssertableLayers` over the ordered layer list, invoking ``callback`` if given."""
        instance = AssertableLayers(layers)
        if callback is not None:
            callback(instance)
        return instance

    def modules(
        self,
        modules: list[str],
        callback: Callable[[AssertableModules], object] | None = None,
    ) -> AssertableModules:
        """Return an :class:`AssertableModules` over the unordered module set, invoking ``callback`` if given."""
        instance = AssertableModules(modules)
        if callback is not None:
            callback(instance)
        return instance


assert_arch = _AssertArch()
