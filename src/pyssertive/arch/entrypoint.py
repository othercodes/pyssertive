from pyssertive.arch.assertable import AssertableArch

__all__ = ["assert_arch"]


def assert_arch(module: str) -> AssertableArch:
    """Return an :class:`AssertableArch` bound to ``module`` for fluent architecture assertions."""
    return AssertableArch(module)
