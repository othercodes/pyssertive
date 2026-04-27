from pyssertive.arch.assertable import AssertableArch


def assert_arch(module: str) -> AssertableArch:
    return AssertableArch(module)
