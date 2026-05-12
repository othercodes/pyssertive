import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_header_should_pass_when_header_value_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.assert_header("X-Custom-Header", "custom-value")
    assert result is response


@pytest.mark.django_db
def test_assert_header_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match="Expected header"):
        response.assert_header("X-Custom-Header", "wrong-value")


@pytest.mark.django_db
def test_assert_header_contains_should_pass_when_fragment_present_in_value(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.assert_header_contains("X-Another-Header", "fragment")
    assert result is response


@pytest.mark.django_db
def test_assert_header_contains_should_raise_when_header_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match=r"Expected header .* to exist"):
        response.assert_header_contains("X-Missing-Header", "fragment")


@pytest.mark.django_db
def test_assert_header_contains_should_raise_when_fragment_absent_from_value(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match="to contain"):
        response.assert_header_contains("X-Custom-Header", "missing")


@pytest.mark.django_db
def test_assert_header_missing_should_pass_when_header_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.assert_header_missing("X-Nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_header_missing_should_raise_when_header_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match="to be missing"):
        response.assert_header_missing("X-Custom-Header")


@pytest.mark.django_db
def test_assert_content_type_should_pass_when_value_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_content_type("application/json")
    assert result is response


@pytest.mark.django_db
def test_assert_content_type_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected Content-Type"):
        response.assert_content_type("text/html")
