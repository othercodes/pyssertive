from __future__ import annotations

import pytest

from pyssertive.adapters.httpx import FluentHttpAssertClient, FluentResponse


def test_client_should_wrap_get_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.get("/json/")
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_post_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.post("/json/", json={"x": 1})
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_put_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.put("/json/", json={"x": 1})
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_patch_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.patch("/json/", json={"x": 1})
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_delete_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.delete("/json/")
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_head_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.head("/json/")
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_options_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.options("/json/")
    assert isinstance(response, FluentResponse)


def test_client_should_wrap_request_response_in_fluent_response(fluent_client: FluentHttpAssertClient):
    response = fluent_client.request("GET", "/json/")
    assert isinstance(response, FluentResponse)


def test_client_should_forward_unknown_attributes_to_wrapped_httpx_client(fluent_client: FluentHttpAssertClient):
    assert fluent_client.base_url == "http://testserver"


def test_client_should_chain_full_assertion_pipeline_on_response(fluent_client: FluentHttpAssertClient):
    fluent_client.get("/json/").assert_ok().assert_content_type("application/json").assert_json_path("method", "GET")


def test_client_get_should_return_404_for_unknown_path(fluent_client: FluentHttpAssertClient):
    fluent_client.get("/nope/").assert_not_found()


def test_client_post_should_echo_request_body(fluent_client_with_body_echo: FluentHttpAssertClient):
    fluent_client_with_body_echo.post("/anywhere/", json={"hello": "world"}).assert_ok().assert_json_path(
        "hello", "world"
    )


def test_client_should_raise_attribute_error_for_unknown_attribute(fluent_client: FluentHttpAssertClient):
    with pytest.raises(AttributeError):
        _ = fluent_client.this_does_not_exist
