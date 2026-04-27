import pytest

from pyssertive.arch import assert_arch


def test_assert_arch_with_callback_should_invoke_it_with_assertable_arch():
    captured: list[object] = []

    assert_arch("clean_pkg.domain", lambda arch: captured.append(arch))

    assert len(captured) == 1


def test_assert_arch_with_callback_should_propagate_assertion_errors_raised_inside():
    with pytest.raises(AssertionError):
        assert_arch(
            "clean_pkg.domain",
            lambda arch: arch.should_only_depend_on(["clean_pkg.domain"]),
        )


def test_module_should_return_scoped_assertable_when_no_callback():
    nested = assert_arch("clean_pkg").module("domain")

    nested.should_only_depend_on("stdlib")


def test_module_should_invoke_callback_with_scoped_assertable_arch():
    assert_arch("clean_pkg").module(
        "domain", lambda d: d.should_only_depend_on("stdlib")
    )


def test_module_should_return_outer_self_after_callback_completes():
    arch = assert_arch("clean_pkg")

    result = arch.module("domain", lambda d: d.should_only_depend_on("stdlib"))

    assert result is arch


def test_module_should_resolve_relative_path_against_current_scope():
    nested = assert_arch("clean_pkg").module("application")

    nested.should_depend_on("clean_pkg.domain")


def test_module_should_accept_absolute_path_when_already_qualified():
    nested = assert_arch("clean_pkg").module("clean_pkg.domain")

    nested.should_only_depend_on("stdlib")


def test_module_should_raise_when_submodule_does_not_exist():
    with pytest.raises(ValueError, match="not in the import graph"):
        assert_arch("clean_pkg").module("nonexistent_xyz")


def test_module_should_raise_clear_error_when_attempting_to_ascend():
    with pytest.raises(ValueError, match="ascend"):
        assert_arch("clean_pkg.application").module("clean_pkg")


def test_module_should_expand_glob_pattern_within_scope():
    assert_arch("glob_pkg").module(
        "*.views", lambda v: v.should_not_depend_on("glob_pkg.bc2.models")
    )


def test_module_should_return_chainable_multi_when_glob_pattern_without_callback():
    assert_arch("glob_pkg").module("*.views").should_not_depend_on(
        "glob_pkg.bc2.models"
    )


def test_module_should_aggregate_failures_across_glob_matches_in_callback():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("glob_pkg").module(
            "*.models", lambda m: m.should_not_depend_on("glob_pkg.*.views")
        )

    message = str(exc_info.value)
    assert "glob_pkg.bc2.models" in message
    assert "glob_pkg.bc3.models" in message


def test_module_should_support_recursive_nesting():
    assert_arch("glob_pkg").module(
        "bc1",
        lambda bc: bc.module(
            "views", lambda v: v.should_only_depend_on("glob_pkg")
        ),
    )


def test_multi_assertable_arch_module_should_descend_into_each_glob_source():
    assert_arch("glob_pkg.bc[123]").module("models").should_not_depend_on(
        "glob_pkg.bc1.views"
    )


def test_multi_assertable_arch_module_should_aggregate_errors_from_callback():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("glob_pkg.bc[123]").module(
            "models",
            lambda m: m.should_not_depend_on("glob_pkg.*.views"),
        )

    message = str(exc_info.value)
    assert "glob_pkg.bc2.models" in message
    assert "glob_pkg.bc3.models" in message


def test_multi_assertable_arch_module_should_resolve_nested_glob_pattern():
    assert_arch("glob_pkg.bc[12]").module(
        "*", lambda m: m.should_not_depend_on("glob_pkg.bc3.models")
    )
