from pyssertive.arch.graph import build_graph


class AssertableArch:
    def __init__(self, module: str) -> None:
        self._module = module
        self._package = module.split(".")[0]

    def should_not_depend_on(self, target: str) -> "AssertableArch":
        graph = build_graph(self._package)
        chain = graph.find_shortest_chain(self._module, target)
        if chain is not None:
            raise AssertionError(
                f"{self._module} should not depend on {target}: " + " → ".join(chain)
            )
        return self
