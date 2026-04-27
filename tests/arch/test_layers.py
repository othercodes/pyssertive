import pytest

from pyssertive.arch import assert_arch


def test_layers_should_return_assertable_layers_instance():
    result = assert_arch.layers(["clean_pkg.domain", "clean_pkg.application"])

    result.should_be_independent()


def test_layers_should_raise_when_layer_module_does_not_exist():
    with pytest.raises(ValueError, match="not in the import graph"):
        assert_arch.layers(["clean_pkg.domain", "clean_pkg.nonexistent_layer"])


def test_layers_should_raise_when_fewer_than_two_layers_provided():
    with pytest.raises(ValueError, match="at least two layers"):
        assert_arch.layers(["clean_pkg.domain"])


def test_should_be_independent_should_pass_when_each_layer_depends_only_on_lower():
    assert_arch.layers([
        "clean_pkg.domain",
        "clean_pkg.application",
        "clean_pkg.infrastructure",
    ]).should_be_independent()


def test_should_be_independent_should_raise_when_lower_layer_imports_higher_layer():
    with pytest.raises(AssertionError):
        assert_arch.layers([
            "dirty_pkg.domain",
            "dirty_pkg.infrastructure",
        ]).should_be_independent()


def test_should_be_independent_should_show_violating_layer_pair_in_error_message():
    with pytest.raises(AssertionError) as exc_info:
        assert_arch.layers([
            "dirty_pkg.domain",
            "dirty_pkg.infrastructure",
        ]).should_be_independent()

    message = str(exc_info.value)
    assert "dirty_pkg.domain" in message
    assert "dirty_pkg.infrastructure" in message


def test_should_be_independent_should_return_self_for_chaining():
    layers = assert_arch.layers([
        "clean_pkg.domain",
        "clean_pkg.application",
    ])

    result = layers.should_be_independent()

    assert result is layers


def test_layers_ignoring_should_grandfather_violation_through_ignored_modules():
    assert_arch.layers([
        "ignoring_pkg.source",
        "ignoring_pkg.forbidden",
    ]).ignoring([
        "ignoring_pkg.legacy.*",
        "ignoring_pkg.modern.*",
    ]).should_be_independent()


def test_layers_ignoring_should_still_raise_when_alternate_non_ignored_path_exists():
    with pytest.raises(AssertionError):
        assert_arch.layers([
            "ignoring_pkg.source",
            "ignoring_pkg.forbidden",
        ]).ignoring("ignoring_pkg.legacy.*").should_be_independent()


def test_layers_ignoring_should_return_self_for_chaining():
    layers = assert_arch.layers(["ignoring_pkg.source", "ignoring_pkg.forbidden"])

    result = layers.ignoring(["foo"])

    assert result is layers


def test_layers_ignoring_should_treat_pair_as_clean_when_importer_layer_fully_ignored():
    assert_arch.layers([
        "ignoring_pkg.source",
        "ignoring_pkg.forbidden",
    ]).ignoring("ignoring_pkg.source").should_be_independent()


def test_layers_should_invoke_callback_with_layers_instance():
    assert_arch.layers(
        [
            "clean_pkg.domain",
            "clean_pkg.application",
            "clean_pkg.infrastructure",
        ],
        lambda layers: layers.should_be_independent(),
    )
