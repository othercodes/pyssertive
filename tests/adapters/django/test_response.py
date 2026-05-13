import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_fluent_response_should_expose_reason_phrase(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    assert response.reason_phrase == "OK"


@pytest.mark.django_db
def test_fluent_response_should_forward_django_specific_attribute(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    assert hasattr(response, "resolver_match")
