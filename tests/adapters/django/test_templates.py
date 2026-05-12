import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_template_used_should_pass_when_template_was_rendered(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    result = response.assert_template_used("test_template.html")
    assert result is response


@pytest.mark.django_db
def test_assert_template_used_should_raise_when_template_was_not_rendered(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError):
        response.assert_template_used("wrong_template.html")


@pytest.mark.django_db
def test_assert_template_not_used_should_pass_when_template_was_not_rendered(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/template/")
    result = response.assert_template_not_used("wrong_template.html")
    assert result is response


@pytest.mark.django_db
def test_assert_template_not_used_should_raise_when_template_was_rendered(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError):
        response.assert_template_not_used("test_template.html")


@pytest.mark.django_db
def test_assert_context_has_should_pass_when_key_present_in_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    result = response.assert_context_has("title")
    assert result is response


@pytest.mark.django_db
def test_assert_context_has_should_raise_when_key_absent_from_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="Expected context to contain"):
        response.assert_context_has("missing_key")


@pytest.mark.django_db
def test_assert_context_has_should_raise_when_response_has_no_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Response has no context"):
        response.assert_context_has("key")


@pytest.mark.django_db
def test_assert_context_equals_should_pass_when_value_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    result = response.assert_context_equals("title", "Test Title")
    assert result is response


@pytest.mark.django_db
def test_assert_context_equals_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="Expected context"):
        response.assert_context_equals("title", "Wrong Title")


@pytest.mark.django_db
def test_assert_context_equals_should_raise_when_response_has_no_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Response has no context"):
        response.assert_context_equals("key", "value")
