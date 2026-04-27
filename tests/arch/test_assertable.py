import pytest

from pyssertive.arch import assert_arch


def test_should_not_depend_on_should_pass_when_module_does_not_import_target():
    assert_arch("clean_pkg.domain").should_not_depend_on("clean_pkg.infrastructure")


def test_should_not_depend_on_should_raise_when_module_directly_imports_target():
    with pytest.raises(AssertionError):
        assert_arch("dirty_pkg.domain").should_not_depend_on("dirty_pkg.infrastructure")
