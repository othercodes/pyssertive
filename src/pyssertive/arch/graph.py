import functools

import grimp


@functools.cache
def build_graph(package: str) -> grimp.ImportGraph:
    try:
        return grimp.build_graph(package, include_external_packages=True)
    except ValueError as exc:
        # grimp raises ValueError when the package cannot be located on
        # sys.path. Translate that to the stdlib ModuleNotFoundError so
        # callers see a familiar exception type. Other ValueErrors are
        # re-raised so unrelated grimp failures aren't masked.
        if "Could not find package" not in str(exc):
            raise
        raise ModuleNotFoundError(str(exc)) from exc
