from pyssertive.arch.assertable import (
    AssertableArch,
    _MultiAssertableArch,
    _expand_glob_source,
    _is_glob_pattern,
)

__all__ = ["assert_arch"]


def assert_arch(module: str) -> AssertableArch | _MultiAssertableArch:
    """
    Return an assertable bound to ``module`` for fluent architecture assertions.

    When ``module`` contains a glob pattern (``*``, ``?``, ``[``), the pattern is
    expanded against the import graph and assertions are applied to every match.
    """
    if _is_glob_pattern(module):
        return _MultiAssertableArch(_expand_glob_source(module))
    return AssertableArch(module)
