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


def test_should_only_depend_on_should_accept_single_string():
    assert_arch("clean_pkg.domain").should_only_depend_on("stdlib")


def test_should_only_depend_on_should_check_transitively_when_directly_false():
    assert_arch("clean_pkg.application").should_only_depend_on(
        ["stdlib", "clean_pkg.domain"], directly=False
    )


def test_should_only_depend_on_should_raise_with_transitive_violation_when_directly_false():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("clean_pkg.application").should_only_depend_on(
            ["clean_pkg.domain"], directly=False
        )

    assert "dataclasses" in str(exc_info.value)


def test_should_depend_on_should_check_only_direct_imports_when_directly_true():
    assert_arch("transitive_pkg.a").should_depend_on("transitive_pkg.b", directly=True)


def test_should_depend_on_should_raise_when_directly_true_and_only_transitive_path_exists():
    with pytest.raises(AssertionError):
        assert_arch("transitive_pkg.a").should_depend_on("transitive_pkg.c", directly=True)


def test_assert_arch_should_raise_when_source_module_not_in_graph():
    with pytest.raises(ValueError, match="not in the import graph"):
        assert_arch("clean_pkg.does_not_exist")


def test_should_not_depend_on_should_raise_when_target_not_in_graph():
    with pytest.raises(ValueError, match="not in the import graph"):
        assert_arch("clean_pkg.domain").should_not_depend_on("totally_unknown_xyz")


def test_should_not_depend_on_should_hint_top_level_when_external_submodule_target():
    with pytest.raises(ValueError, match="top-level"):
        assert_arch("clean_pkg.domain").should_not_depend_on("dataclasses.dataclass")


def test_assert_arch_should_suggest_close_match_when_source_typo():
    with pytest.raises(ValueError, match="Did you mean 'clean_pkg.domain'"):
        assert_arch("clean_pkg.domian")


def test_should_not_depend_on_should_suggest_close_match_when_target_typo():
    with pytest.raises(ValueError, match="Did you mean 'clean_pkg.application'"):
        assert_arch("clean_pkg.domain").should_not_depend_on("clean_pkg.applicaton")


def test_assert_arch_should_expand_glob_pattern_and_apply_should_not_depend_on_to_each_match():
    assert_arch("glob_pkg.*.views").should_not_depend_on("glob_pkg.bc2.models")


def test_assert_arch_should_aggregate_assertion_errors_per_glob_match():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("glob_pkg.*.models").should_not_depend_on("glob_pkg.*.views")

    message = str(exc_info.value)
    assert "glob_pkg.bc2.models" in message
    assert "glob_pkg.bc3.models" in message


def test_multi_assertable_dispatcher_should_label_each_failing_source_in_aggregated_message():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("glob_pkg.*.models").should_not_depend_on("glob_pkg.*.views")

    message = str(exc_info.value)
    assert "glob_pkg.bc2.models should not depend on" in message
    assert "glob_pkg.bc3.models should not depend on" in message


def test_assert_arch_should_raise_when_source_glob_matches_no_modules():
    with pytest.raises(ValueError, match="did not match any module"):
        assert_arch("glob_pkg.*.nonexistent_xyz")


def test_assert_arch_should_raise_when_source_glob_top_level_is_a_pattern():
    with pytest.raises(ValueError, match="fixed top-level"):
        assert_arch("*.models")


def test_should_not_depend_on_should_expand_glob_target():
    with pytest.raises(AssertionError):
        assert_arch("glob_pkg.bc2.models").should_not_depend_on("glob_pkg.*.views")


def test_should_not_depend_on_should_raise_when_target_glob_matches_no_modules():
    with pytest.raises(ValueError, match="did not match any module"):
        assert_arch("glob_pkg.bc1.models").should_not_depend_on("glob_pkg.*.nonexistent_xyz")


def test_assert_arch_glob_should_expose_should_depend_on():
    assert_arch("glob_pkg.bc[1].views").should_depend_on("glob_pkg.bc1.models")


def test_assert_arch_glob_should_expose_should_only_depend_on_with_ignoring():
    assert_arch("glob_pkg.*.views")\
        .ignoring(["glob_pkg.bc1.unused"])\
        .should_only_depend_on(["glob_pkg"])


def test_should_only_depend_on_should_not_treat_user_module_named_stdlib_as_token():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("user_stdlib_pkg.consumer").should_only_depend_on(["stdlib"])

    assert "user_stdlib_pkg.stdlib" in str(exc_info.value)


def test_ignoring_should_pass_when_all_chain_paths_pass_through_ignored_modules():
    assert_arch("ignoring_pkg.source").ignoring(
        ["ignoring_pkg.legacy.via", "ignoring_pkg.modern.via"]
    ).should_not_depend_on("ignoring_pkg.forbidden")


def test_ignoring_should_accept_glob_pattern():
    assert_arch("ignoring_pkg.source").ignoring(
        ["ignoring_pkg.legacy.*", "ignoring_pkg.modern.*"]
    ).should_not_depend_on("ignoring_pkg.forbidden")


def test_ignoring_should_accept_single_string_pattern():
    arch = assert_arch("ignoring_pkg.source")

    result = arch.ignoring("ignoring_pkg.legacy.*")

    assert result is arch


def test_ignoring_should_still_detect_violation_via_alternate_path():
    with pytest.raises(AssertionError):
        assert_arch("ignoring_pkg.source").ignoring(
            "ignoring_pkg.legacy.*"
        ).should_not_depend_on("ignoring_pkg.forbidden")


def test_ignoring_should_return_self_for_chaining():
    arch = assert_arch("ignoring_pkg.source")

    result = arch.ignoring(["ignoring_pkg.legacy.*"])

    assert result is arch


def test_ignoring_should_filter_violations_in_should_only_depend_on():
    assert_arch("ignoring_pkg.source").ignoring(
        ["ignoring_pkg.legacy.*", "ignoring_pkg.modern.*"]
    ).should_only_depend_on(["ignoring_pkg"])


def test_should_only_depend_on_should_skip_modules_only_reachable_via_ignored_paths():
    assert_arch("ignoring_pkg.source").ignoring(
        ["ignoring_pkg.legacy.*", "ignoring_pkg.modern.*"]
    ).should_only_depend_on(
        ["ignoring_pkg.source", "ignoring_pkg.forbidden_direct"],
        directly=False,
    )


def test_should_only_depend_on_should_still_flag_dep_reachable_without_ignored_path():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch("ignoring_pkg.source").ignoring(
            ["ignoring_pkg.legacy.*", "ignoring_pkg.modern.*"]
        ).should_only_depend_on(["ignoring_pkg.source"], directly=False)

    assert "ignoring_pkg.forbidden_direct" in str(exc_info.value)


def test_should_not_depend_on_should_pass_when_source_module_is_ignored():
    assert_arch("ignoring_pkg.legacy.via").ignoring(
        "ignoring_pkg.legacy.*"
    ).should_not_depend_on("ignoring_pkg.forbidden")


def test_should_only_depend_on_should_pass_when_source_module_is_ignored():
    assert_arch("ignoring_pkg.legacy.via").ignoring(
        "ignoring_pkg.legacy.*"
    ).should_only_depend_on(["nothing"], directly=False)


def test_should_not_depend_on_should_handle_cyclic_imports_without_infinite_loop():
    assert_arch("cycle_pkg.a").ignoring("nothing_to_match").should_not_depend_on(
        "cycle_pkg.unrelated"
    )


def test_should_not_depend_on_should_treat_package_target_as_any_descendant():
    with pytest.raises(AssertionError):
        assert_arch("ignoring_pkg.source").should_not_depend_on("ignoring_pkg.legacy")


def test_should_depend_on_should_treat_package_target_as_any_descendant():
    assert_arch("ignoring_pkg.source").should_depend_on("ignoring_pkg.legacy")


def test_should_not_depend_on_with_ignoring_should_treat_package_target_as_any_descendant():
    with pytest.raises(AssertionError):
        assert_arch("ignoring_pkg.source").ignoring(
            "ignoring_pkg.modern.*"
        ).should_not_depend_on("ignoring_pkg.legacy")
