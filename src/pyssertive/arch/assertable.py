from pyssertive.arch.graph import build_graph


class AssertableArch:
    def __init__(self, module: str) -> None:
        self._module = module
        self._package = module.split(".")[0]

    def should_not_depend_on(
        self, target: str | list[str], directly: bool = False
    ) -> "AssertableArch":
        targets = [target] if isinstance(target, str) else list(target)
        graph = build_graph(self._package)
        violations: list[str] = []
        for candidate in targets:
            if directly:
                if candidate in graph.find_modules_directly_imported_by(self._module):
                    violations.append(f"{candidate} (direct import)")
            else:
                chain = graph.find_shortest_chain(self._module, candidate)
                if chain is not None:
                    violations.append(f"{candidate}: " + " → ".join(chain))
        if violations:
            raise AssertionError(
                f"{self._module} should not depend on:\n  - " + "\n  - ".join(violations)
            )
        return self
