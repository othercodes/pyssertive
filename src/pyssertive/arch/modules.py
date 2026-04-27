import fnmatch
from collections import deque

import grimp

from pyssertive.arch.graph import build_graph

__all__ = ["AssertableModules"]


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
            raise ValueError(
                "assert_arch.modules requires at least two modules."
            )
        self._modules = list(modules)
        self._package = modules[0].split(".")[0]
        graph = build_graph(self._package)
        for module in self._modules:
            if module not in graph.modules:
                raise ValueError(
                    f"Module {module!r} is not in the import graph for "
                    f"package {self._package!r}."
                )
        self._ignored: list[str] = []

    def ignoring(self, patterns: str | list[str]) -> "AssertableModules":
        """Add fnmatch glob patterns excluded from cross-import detection."""
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
                chain = self._find_cross_chain(graph, src, dst)
                if chain is not None:
                    violations.append(f"{src} → {dst}: " + " → ".join(chain))
        if violations:
            raise AssertionError(
                "Modules are not isolated:\n  - " + "\n  - ".join(violations)
            )
        return self

    def _is_ignored(self, module: str) -> bool:
        return any(fnmatch.fnmatch(module, pattern) for pattern in self._ignored)

    def _find_cross_chain(
        self, graph: grimp.ImportGraph, importer: str, imported: str
    ) -> tuple[str, ...] | None:
        if not self._ignored:
            chains = graph.find_shortest_chains(
                importer=importer, imported=imported, as_packages=True
            )
            if chains:
                return sorted(chains)[0]
            return None
        importer_modules = {importer} | graph.find_descendants(importer)
        imported_modules = {imported} | graph.find_descendants(imported)
        sources = [m for m in importer_modules if not self._is_ignored(m)]
        if not sources:
            return None
        visited: set[str] = set(sources)
        queue: deque[tuple[str, tuple[str, ...]]] = deque(
            (s, (s,)) for s in sources
        )
        while queue:
            current, path = queue.popleft()
            for next_mod in graph.find_modules_directly_imported_by(current):
                if next_mod in visited or self._is_ignored(next_mod):
                    continue
                new_path = (*path, next_mod)
                if next_mod in imported_modules:
                    return new_path
                visited.add(next_mod)
                queue.append((next_mod, new_path))
        return None
