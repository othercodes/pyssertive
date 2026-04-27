import fnmatch
import sys
from collections import deque

import grimp

from pyssertive.arch.graph import build_graph

_STDLIB_TOKEN = "stdlib"

__all__ = ["AssertableArch"]


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
    instead of producing cryptic engine errors mid-assertion.
    """

    def __init__(self, module: str) -> None:
        self._module = module
        self._package = module.split(".")[0]
        graph = build_graph(self._package)
        if module not in graph.modules:
            raise ValueError(
                f"Source module {module!r} is not in the import graph for "
                f"package {self._package!r}."
            )
        self._ignored: list[str] = []

    def ignoring(self, patterns: str | list[str]) -> "AssertableArch":
        new_patterns = [patterns] if isinstance(patterns, str) else list(patterns)
        self._ignored.extend(new_patterns)
        return self

    def should_depend_on(
        self, target: str | list[str], directly: bool = False
    ) -> "AssertableArch":
        targets = [target] if isinstance(target, str) else list(target)
        graph = build_graph(self._package)
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
        targets = [target] if isinstance(target, str) else list(target)
        graph = build_graph(self._package)
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
        allowed_list = [allowed] if isinstance(allowed, str) else list(allowed)
        graph = build_graph(self._package)
        if directly:
            deps = graph.find_modules_directly_imported_by(self._module)
        else:
            deps = graph.find_upstream_modules(self._module)
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
            self._raise_violations(f"should only depend on {allowed_list}, but also imports", violations)
        return self

    def _validate_target(self, target: str, graph: grimp.ImportGraph) -> None:
        if target in graph.modules:
            return
        top = target.split(".")[0]
        if top in graph.modules:
            raise ValueError(
                f"Target {target!r} is not a node in the graph. External "
                f"submodules are tracked at the top-level only — use "
                f"{top!r} instead."
            )
        raise ValueError(
            f"Target {target!r} is not in the import graph for "
            f"package {self._package!r}."
        )

    def _raise_violations(self, action: str, items: list[str]) -> None:
        raise AssertionError(
            f"{self._module} {action}:\n  - " + "\n  - ".join(items)
        )

    def _is_ignored(self, module: str) -> bool:
        return any(fnmatch.fnmatch(module, pattern) for pattern in self._ignored)

    def _find_chain(self, graph: grimp.ImportGraph, target: str) -> tuple[str, ...] | None:
        if not self._ignored:
            return graph.find_shortest_chain(self._module, target)
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
