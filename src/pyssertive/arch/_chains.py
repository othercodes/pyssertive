import fnmatch
from collections import deque

import grimp

__all__ = ["find_chain", "find_package_chain", "find_upstream", "is_ignored"]


def is_ignored(module: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(module, pattern) for pattern in patterns)


def find_chain(
    graph: grimp.ImportGraph,
    source: str,
    target: str,
    ignored: list[str],
) -> tuple[str, ...] | None:
    if not ignored:
        return graph.find_shortest_chain(source, target)
    if is_ignored(source, ignored):
        return None
    visited = {source}
    queue: deque[tuple[str, tuple[str, ...]]] = deque([(source, (source,))])
    while queue:
        current, path = queue.popleft()
        for next_mod in graph.find_modules_directly_imported_by(current):
            if next_mod in visited or is_ignored(next_mod, ignored):
                continue
            new_path = (*path, next_mod)
            if next_mod == target:
                return new_path
            visited.add(next_mod)
            queue.append((next_mod, new_path))
    return None


def find_upstream(
    graph: grimp.ImportGraph,
    source: str,
    ignored: list[str],
) -> set[str]:
    if not ignored:
        return set(graph.find_upstream_modules(source))
    if is_ignored(source, ignored):
        return set()
    visited = {source}
    queue: deque[str] = deque([source])
    upstream: set[str] = set()
    while queue:
        current = queue.popleft()
        for next_mod in graph.find_modules_directly_imported_by(current):
            if next_mod in visited or is_ignored(next_mod, ignored):
                continue
            visited.add(next_mod)
            upstream.add(next_mod)
            queue.append(next_mod)
    return upstream


def find_package_chain(
    graph: grimp.ImportGraph,
    importer: str,
    imported: str,
    ignored: list[str],
) -> tuple[str, ...] | None:
    if not ignored:
        chains = graph.find_shortest_chains(
            importer=importer, imported=imported, as_packages=True
        )
        if chains:
            return sorted(chains)[0]
        return None
    importer_modules = {importer} | graph.find_descendants(importer)
    imported_modules = {imported} | graph.find_descendants(imported)
    sources = [m for m in importer_modules if not is_ignored(m, ignored)]
    if not sources:
        return None
    visited: set[str] = set(sources)
    queue: deque[tuple[str, tuple[str, ...]]] = deque(
        (s, (s,)) for s in sources
    )
    while queue:
        current, path = queue.popleft()
        for next_mod in graph.find_modules_directly_imported_by(current):
            if next_mod in visited or is_ignored(next_mod, ignored):
                continue
            new_path = (*path, next_mod)
            if next_mod in imported_modules:
                return new_path
            visited.add(next_mod)
            queue.append((next_mod, new_path))
    return None
