from collections.abc import Callable

from pyssertive.arch.assertable import (
    AssertableArch,
    _MultiAssertableArch,
    _expand_glob_source,
    _is_glob_pattern,
)

__all__ = ["assert_arch"]


def assert_arch(
    module: str,
    callback: Callable[[AssertableArch | _MultiAssertableArch], object] | None = None,
) -> AssertableArch | _MultiAssertableArch:
    """
    Return an assertable bound to ``module`` for fluent architecture assertions.

    When ``module`` contains a glob pattern (``*``, ``?``, ``[``), the pattern
    is expanded against the import graph and assertions are applied to every
    match. When ``callback`` is given it is invoked with the assertable so
    callers can scope a block of assertions Pest-style.
    """
    arch: AssertableArch | _MultiAssertableArch
    if _is_glob_pattern(module):
        arch = _MultiAssertableArch(_expand_glob_source(module))
    else:
        arch = AssertableArch(module)
    if callback is not None:
        callback(arch)
    return arch
