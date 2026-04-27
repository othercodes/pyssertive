import pytest

from pyssertive.arch.graph import build_graph


def test_build_graph_should_return_module_graph_for_package():
    graph = build_graph("clean_pkg")

    assert "clean_pkg" in graph.modules
    assert "clean_pkg.domain" in graph.modules
    assert "clean_pkg.application" in graph.modules
    assert "clean_pkg.infrastructure" in graph.modules


def test_build_graph_should_cache_graph_per_package_in_same_session():
    first = build_graph("clean_pkg")
    second = build_graph("clean_pkg")

    assert first is second


def test_build_graph_should_build_separate_graph_per_package():
    clean = build_graph("clean_pkg")
    dirty = build_graph("dirty_pkg")

    assert clean is not dirty
    assert "clean_pkg" in clean.modules
    assert "dirty_pkg" in dirty.modules


def test_build_graph_should_raise_when_package_is_not_importable():
    with pytest.raises(ModuleNotFoundError):
        build_graph("definitely_not_a_real_package_xyz")
