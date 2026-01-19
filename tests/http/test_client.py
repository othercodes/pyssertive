import pytest

from pyssertive.http.client import FluentResponse


@pytest.mark.django_db
def test_fluent_response_wrapped_property(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    assert response.wrapped is not None
    assert response.wrapped.status_code == 200


@pytest.mark.django_db
def test_fluent_response_proxies_attributes(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    assert response.status_code == 200
    assert response.content is not None


@pytest.mark.django_db
def test_fluent_response_explicit_properties(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    assert response.headers is not None
    assert response.cookies is not None
    assert response.charset is not None
    assert response.reason_phrase == "OK"


@pytest.mark.django_db
def test_fluent_response_getattr_fallback(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    assert hasattr(response, "resolver_match")


@pytest.mark.django_db
def test_client_post(fluent_admin_client):
    response = fluent_admin_client.post("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_put(fluent_admin_client):
    response = fluent_admin_client.put("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_patch(fluent_admin_client):
    response = fluent_admin_client.patch("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_delete(fluent_admin_client):
    response = fluent_admin_client.delete("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_head(fluent_admin_client):
    response = fluent_admin_client.head("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_options(fluent_admin_client):
    response = fluent_admin_client.options("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_trace(fluent_admin_client):
    response = fluent_admin_client.trace("/json/")
    assert isinstance(response, FluentResponse)


@pytest.mark.django_db
def test_client_proxies_attributes(fluent_admin_client):
    session = fluent_admin_client.session
    assert session is not None


@pytest.mark.django_db
def test_fluent_chaining(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_ok().assert_json().assert_json_path("ok", True).assert_content_type("application/json")
    assert result is response
