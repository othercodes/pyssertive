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


def test_should_depend_on_should_pass_when_module_directly_imports_target():
    assert_arch("clean_pkg.application").should_depend_on("clean_pkg.domain")


def test_should_depend_on_should_pass_when_dependency_is_transitive():
    assert_arch("transitive_pkg.a").should_depend_on("transitive_pkg.c")


def test_should_depend_on_should_raise_when_target_is_not_imported():
    with pytest.raises(AssertionError):
        assert_arch("clean_pkg.domain").should_depend_on("clean_pkg.infrastructure")


def test_should_depend_on_should_include_module_and_target_in_error_message():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("clean_pkg.domain").should_depend_on("clean_pkg.infrastructure")

    message = str(exc_info.value)
    assert "clean_pkg.domain" in message
    assert "clean_pkg.infrastructure" in message


def test_should_depend_on_should_return_self_for_chaining():
    arch = assert_arch("clean_pkg.application")

    result = arch.should_depend_on("clean_pkg.domain")

    assert result is arch


def test_should_depend_on_should_accept_list_of_targets():
    assert_arch("clean_pkg.infrastructure").should_depend_on(
        ["clean_pkg.domain", "clean_pkg.application"]
    )


def test_should_depend_on_should_raise_listing_all_missing_targets_when_list_partially_satisfied():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("transitive_pkg.a").should_depend_on(
            ["transitive_pkg.b", "transitive_pkg.d"]
        )

    message = str(exc_info.value)
    assert "transitive_pkg.d" in message
    assert "transitive_pkg.b" not in message


def test_should_only_depend_on_should_pass_when_all_imports_are_in_allowlist():
    assert_arch("clean_pkg.application").should_only_depend_on(["clean_pkg.domain"])


def test_should_only_depend_on_should_pass_when_module_only_uses_stdlib_and_stdlib_token_listed():
    assert_arch("clean_pkg.domain").should_only_depend_on(["stdlib"])


def test_should_only_depend_on_should_treat_stdlib_token_as_any_python_stdlib_module():
    assert_arch("stdlib_pkg.wide").should_only_depend_on(["stdlib"])


def test_should_only_depend_on_should_raise_when_module_imports_unlisted_package():
    with pytest.raises(AssertionError):
        assert_arch("clean_pkg.application").should_only_depend_on(["stdlib"])


def test_should_only_depend_on_should_list_all_violating_imports_in_error_message():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("clean_pkg.application").should_only_depend_on(["stdlib"])

    message = str(exc_info.value)
    assert "clean_pkg.domain" in message


def test_should_only_depend_on_should_raise_for_stdlib_imports_when_stdlib_token_not_in_allowlist():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("clean_pkg.domain").should_only_depend_on(["clean_pkg.domain"])

    message = str(exc_info.value)
    assert "dataclasses" in message


def test_should_only_depend_on_should_return_self_for_chaining():
    arch = assert_arch("clean_pkg.application")

    result = arch.should_only_depend_on(["clean_pkg.domain"])

    assert result is arch
