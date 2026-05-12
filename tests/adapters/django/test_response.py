import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_fluent_response_should_expose_wrapped_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    assert response.wrapped is not None
    assert response.wrapped.status_code == 200


@pytest.mark.django_db
def test_fluent_response_should_proxy_protocol_properties(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    assert response.status_code == 200
    assert response.content is not None


@pytest.mark.django_db
def test_fluent_response_should_expose_django_response_properties(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    assert response.headers is not None
    assert response.cookies is not None
    assert response.charset is not None
    assert response.reason_phrase == "OK"


@pytest.mark.django_db
def test_fluent_response_should_forward_unknown_attributes_to_wrapped_response(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    assert hasattr(response, "resolver_match")


@pytest.mark.django_db
def test_fluent_response_should_return_self_for_method_chaining(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_ok().assert_json_path("ok", True).assert_content_type("application/json")
    assert result is response
