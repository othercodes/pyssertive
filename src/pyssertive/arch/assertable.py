from pyssertive.arch.graph import build_graph


class AssertableArch:
    def __init__(self, module: str) -> None:
        self._module = module
        self._package = module.split(".")[0]

    def should_depend_on(self, target: str | list[str]) -> "AssertableArch":
        targets = [target] if isinstance(target, str) else list(target)
        graph = build_graph(self._package)
        missing: list[str] = []
        for candidate in targets:
            if graph.find_shortest_chain(self._module, candidate) is None:
                missing.append(candidate)
        if missing:
            raise AssertionError(
                f"{self._module} should depend on:\n  - " + "\n  - ".join(missing)
            )
        return self

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
