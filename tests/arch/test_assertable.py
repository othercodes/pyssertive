import pytest

from pyssertive.arch import assert_arch


def test_should_not_depend_on_should_pass_when_module_does_not_import_target():
    assert_arch("clean_pkg.domain").should_not_depend_on("clean_pkg.infrastructure")


def test_should_not_depend_on_should_raise_when_module_directly_imports_target():
    with pytest.raises(AssertionError):
        assert_arch("dirty_pkg.domain").should_not_depend_on("dirty_pkg.infrastructure")


def test_should_not_depend_on_should_raise_when_module_transitively_imports_target():
    with pytest.raises(AssertionError):
        assert_arch("transitive_pkg.a").should_not_depend_on("transitive_pkg.c")


def test_should_not_depend_on_should_include_import_chain_in_error_message():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("transitive_pkg.a").should_not_depend_on("transitive_pkg.c")

    message = str(exc_info.value)
    assert "transitive_pkg.a" in message
    assert "transitive_pkg.b" in message
    assert "transitive_pkg.c" in message
    assert "→" in message


def test_should_not_depend_on_should_return_self_for_chaining():
    arch = assert_arch("clean_pkg.domain")

    result = arch.should_not_depend_on("clean_pkg.infrastructure")

    assert result is arch


def test_should_not_depend_on_should_ignore_transitive_when_directly_true():
    assert_arch("transitive_pkg.a").should_not_depend_on("transitive_pkg.c", directly=True)


def test_should_not_depend_on_should_raise_when_directly_true_and_module_directly_imports_target():
    with pytest.raises(AssertionError):
        assert_arch("dirty_pkg.domain").should_not_depend_on("dirty_pkg.infrastructure", directly=True)


def test_should_not_depend_on_should_accept_list_of_targets():
    assert_arch("clean_pkg.domain").should_not_depend_on(
        ["clean_pkg.application", "clean_pkg.infrastructure"]
    )


def test_should_not_depend_on_should_aggregate_violations_across_list_in_error_message():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("transitive_pkg.a").should_not_depend_on(
            ["transitive_pkg.b", "transitive_pkg.c"]
        )

    message = str(exc_info.value)
    assert "transitive_pkg.b" in message
    assert "transitive_pkg.c" in message
