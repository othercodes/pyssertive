import pytest

from pyssertive.arch import assert_arch


def test_modules_should_return_assertable_modules_instance():
    result = assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc5"])

    result.should_be_isolated()


def test_modules_should_raise_when_a_module_does_not_exist():
    with pytest.raises(ValueError, match="not in the import graph"):
        assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.fake_xyz"])


def test_modules_should_raise_when_fewer_than_two_modules_provided():
    with pytest.raises(ValueError, match="at least two modules"):
        assert_arch.modules(["bcs_pkg.bc1"])


def test_should_be_isolated_should_pass_when_no_module_imports_another_in_set():
    assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc5"]).should_be_isolated()


def test_should_be_isolated_should_raise_when_one_module_directly_imports_another():
    with pytest.raises(AssertionError):
        assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc2"]).should_be_isolated()


def test_should_be_isolated_should_raise_when_modules_have_transitive_link():
    with pytest.raises(AssertionError):
        assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc3"]).should_be_isolated()


def test_should_be_isolated_should_show_violating_pair_with_import_chain_in_error():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc2"]).should_be_isolated()

    message = str(exc_info.value)
    assert "bcs_pkg.bc1" in message
    assert "bcs_pkg.bc2" in message


def test_should_be_isolated_should_pass_when_violations_are_only_through_ignored_paths():
    assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc4"]).ignoring(["*.events"]).should_be_isolated()


def test_should_be_isolated_should_still_detect_alternate_non_ignored_chain():
    with pytest.raises(AssertionError):
        assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc6"]).ignoring(["*.events"]).should_be_isolated()


def test_should_be_isolated_should_treat_pair_as_isolated_when_importer_fully_ignored():
    assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc4"]).ignoring(["bcs_pkg.bc4", "bcs_pkg.bc4.*"]).should_be_isolated()


def test_should_be_isolated_should_return_self_for_chaining():
    modules = assert_arch.modules(["bcs_pkg.bc1", "bcs_pkg.bc5"])

    result = modules.should_be_isolated()

    assert result is modules


def test_modules_should_invoke_callback_with_modules_instance():
    assert_arch.modules(
        ["bcs_pkg.bc1", "bcs_pkg.bc5"],
        lambda modules: modules.should_be_isolated(),
    )
