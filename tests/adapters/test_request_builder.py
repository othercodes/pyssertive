from __future__ import annotations

import pytest

from tests.adapters._factories import REQUEST_BUILDER_ADAPTERS, inspect


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_apply_method_in_uppercase(make_builder):
    snapshot = inspect(make_builder().with_method("post").build())
    assert snapshot["method"] == "POST"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_apply_path(make_builder):
    snapshot = inspect(make_builder().with_path("/api/users/").build())
    assert snapshot["path"] == "/api/users/"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_apply_single_header(make_builder):
    snapshot = inspect(make_builder().with_header("X-Trace", "abc").build())
    assert snapshot["headers"].get("x-trace") == "abc"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_merge_multiple_headers(make_builder):
    snapshot = inspect(make_builder().with_header("X-A", "1").with_headers({"X-B": "2", "X-A": "1b"}).build())
    assert snapshot["headers"].get("x-a") == "1b"
    assert snapshot["headers"].get("x-b") == "2"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_apply_single_cookie_as_string(make_builder):
    snapshot = inspect(make_builder().with_cookie("session", 7).build())
    assert snapshot["cookies"].get("session") == "7"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_apply_multiple_cookies(make_builder):
    snapshot = inspect(make_builder().with_cookies({"a": 1, "b": "x"}).build())
    assert snapshot["cookies"].get("a") == "1"
    assert snapshot["cookies"].get("b") == "x"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_merge_query_parameters(make_builder):
    snapshot = inspect(make_builder().with_query_string({"page": "1"}).with_query_string({"size": "10"}).build())
    assert snapshot["query"].get("page") == "1"
    assert snapshot["query"].get("size") == "10"


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_record_dict_body(make_builder):
    snapshot = inspect(make_builder().with_method("POST").with_body({"name": "Alice"}).build())
    body = snapshot["body"]
    body_text = body.decode("utf-8") if isinstance(body, bytes) else repr(body)
    assert "Alice" in body_text


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_return_self_for_chaining(make_builder):
    builder = make_builder()
    assert builder.with_method("POST") is builder
    assert builder.with_path("/x/") is builder
    assert builder.with_header("X", "y") is builder
    assert builder.with_headers({"A": "1"}) is builder
    assert builder.with_cookie("c", "1") is builder
    assert builder.with_cookies({"d": "2"}) is builder
    assert builder.with_query_string({"q": "1"}) is builder
    assert builder.with_body({"k": "v"}) is builder


@pytest.mark.parametrize("make_builder", REQUEST_BUILDER_ADAPTERS)
def test_request_builder_should_chain_full_request_specification(make_builder):
    snapshot = inspect(
        make_builder()
        .with_method("POST")
        .with_path("/api/users/")
        .with_header("Content-Type", "application/json")
        .with_header("X-Request-Id", "req-1")
        .with_cookie("session", "abc")
        .with_query_string({"include": "profile"})
        .with_body({"name": "Alice"})
        .build()
    )
    assert snapshot["method"] == "POST"
    assert snapshot["path"] == "/api/users/"
    assert snapshot["headers"].get("content-type", "").startswith("application/json")
    assert snapshot["cookies"].get("session") == "abc"
    assert snapshot["query"].get("include") == "profile"
