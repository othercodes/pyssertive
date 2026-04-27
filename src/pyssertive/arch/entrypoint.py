from collections.abc import Callable

from pyssertive.arch.assertable import (
    AssertableArch,
    _MultiAssertableArch,
    _expand_glob_source,
    _is_glob_pattern,
)
from pyssertive.arch.layers import AssertableLayers
from pyssertive.arch.modules import AssertableModules

__all__ = ["assert_arch"]


class _AssertArch:
    """
    Callable entrypoint to architecture assertions.

    Invoke with a module path to obtain an :class:`AssertableArch`;
    call :meth:`layers` to obtain an :class:`AssertableLayers` for
    layered architecture rules.
    """

    def __call__(
        self,
        module: str,
        callback: Callable[[AssertableArch | _MultiAssertableArch], object] | None = None,
    ) -> AssertableArch | _MultiAssertableArch:
        """
        Return an assertable bound to ``module``. Glob patterns expand
        across the import graph. When ``callback`` is given it is
        invoked with the assertable so callers can scope a block of
        assertions Pest-style.
        """
        arch: AssertableArch | _MultiAssertableArch
        if _is_glob_pattern(module):
            arch = _MultiAssertableArch(_expand_glob_source(module))
        else:
            arch = AssertableArch(module)
        if callback is not None:
            callback(arch)
        return arch

    def layers(
        self,
        layers: list[str],
        callback: Callable[[AssertableLayers], object] | None = None,
    ) -> AssertableLayers:
        """Return an :class:`AssertableLayers` over the ordered layer list, invoking ``callback`` if given."""
        instance = AssertableLayers(layers)
        if callback is not None:
            callback(instance)
        return instance

    def modules(
        self,
        modules: list[str],
        callback: Callable[[AssertableModules], object] | None = None,
    ) -> AssertableModules:
        """Return an :class:`AssertableModules` over the unordered module set, invoking ``callback`` if given."""
        instance = AssertableModules(modules)
        if callback is not None:
            callback(instance)
        return instance


assert_arch = _AssertArch()
