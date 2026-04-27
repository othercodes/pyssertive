from pyssertive.arch.graph import build_graph


def test_build_graph_should_return_module_graph_for_package():
    graph = build_graph("clean_pkg")

    assert "clean_pkg" in graph.modules
    assert "clean_pkg.domain" in graph.modules
    assert "clean_pkg.application" in graph.modules
    assert "clean_pkg.infrastructure" in graph.modules
