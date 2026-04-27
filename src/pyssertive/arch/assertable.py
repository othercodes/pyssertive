import sys

from pyssertive.arch.graph import build_graph

_STDLIB_TOKEN = "stdlib"


class AssertableArch:
    def __init__(self, module: str) -> None:
        self._module = module
        self._package = module.split(".")[0]

    def should_only_depend_on(self, allowed: list[str]) -> "AssertableArch":
        graph = build_graph(self._package)
        deps = graph.find_modules_directly_imported_by(self._module)
        stdlib_allowed = _STDLIB_TOKEN in allowed
        explicit = [a for a in allowed if a != _STDLIB_TOKEN]
        violations = [
            dep
            for dep in deps
            if not (stdlib_allowed and dep.split(".")[0] in sys.stdlib_module_names)
            and not any(dep == a or dep.startswith(f"{a}.") for a in explicit)
        ]
        if violations:
            raise AssertionError(
                f"{self._module} should only depend on {allowed}, but also imports:\n  - "
                + "\n  - ".join(sorted(violations))
            )
        return self

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
