from pyssertive.arch._chains import find_package_chain
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
