import functools

import grimp


@functools.cache
def build_graph(package: str) -> grimp.ImportGraph:
    try:
        return grimp.build_graph(package)
    except ValueError as exc:
        raise ModuleNotFoundError(str(exc)) from exc
