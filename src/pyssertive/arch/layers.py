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

    def should_be_independent(self) -> "AssertableLayers":
        """Assert each layer only depends on layers preceding it in the list."""
        graph = build_graph(self._package)
        violations: list[str] = []
        for i, lower in enumerate(self._layers):
            for higher in self._layers[i + 1:]:
                chains = graph.find_shortest_chains(
                    importer=lower, imported=higher, as_packages=True
                )
                if chains:
                    chain = sorted(chains)[0]
                    violations.append(
                        f"{lower} → {higher}: " + " → ".join(chain)
                    )
        if violations:
            raise AssertionError(
                "Layered architecture violations (each layer must depend "
                "only on prior layers):\n  - " + "\n  - ".join(violations)
            )
        return self
