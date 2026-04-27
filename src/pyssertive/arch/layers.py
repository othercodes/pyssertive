import fnmatch
from collections import deque

import grimp

from pyssertive.arch.graph import build_graph

__all__ = ["AssertableLayers"]


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
            raise ValueError(
                "assert_arch.layers requires at least two layers."
            )
        self._layers = list(layers)
        self._package = layers[0].split(".")[0]
        graph = build_graph(self._package)
        for layer in self._layers:
            if layer not in graph.modules:
                raise ValueError(
                    f"Layer {layer!r} is not in the import graph for "
                    f"package {self._package!r}."
                )
        self._ignored: list[str] = []

    def ignoring(self, patterns: str | list[str]) -> "AssertableLayers":
        """Add fnmatch glob patterns excluded from chain traversal."""
        new_patterns = [patterns] if isinstance(patterns, str) else list(patterns)
        self._ignored.extend(new_patterns)
        return self

    def should_be_independent(self) -> "AssertableLayers":
        """Assert each layer only depends on layers preceding it in the list."""
        graph = build_graph(self._package)
        violations: list[str] = []
        for i, lower in enumerate(self._layers):
            for higher in self._layers[i + 1:]:
                chain = self._find_chain_between(graph, lower, higher)
                if chain is not None:
                    violations.append(
                        f"{lower} → {higher}: " + " → ".join(chain)
                    )
        if violations:
            raise AssertionError(
                "Layered architecture violations (each layer must depend "
                "only on prior layers):\n  - " + "\n  - ".join(violations)
            )
        return self

    def _is_ignored(self, module: str) -> bool:
        return any(fnmatch.fnmatch(module, pattern) for pattern in self._ignored)

    def _find_chain_between(
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
