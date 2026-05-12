import pytest

from pyssertive.adapters.django import FluentHttpAssertClient, FluentResponse


@pytest.mark.django_db
def test_client_should_wrap_post_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.post("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_wrap_put_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.put("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_wrap_patch_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.patch("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_wrap_delete_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.delete("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_wrap_head_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.head("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_wrap_options_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.options("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_wrap_trace_response_in_fluent_response(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.trace("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_should_forward_unknown_attributes_to_wrapped_django_client(fluent_admin_client: FluentHttpAssertClient):
    session = fluent_admin_client.session
    assert session is not None
