import pytest
from django.http import HttpResponse

from pyssertive.adapters.django import FluentHttpAssertClient, FluentResponse


@pytest.mark.django_db
def test_assert_session_has_should_pass_when_key_present_in_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_has("user_id")
    assert result is response


@pytest.mark.django_db
def test_assert_session_has_should_pass_when_key_and_value_match(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_has("user_id", 123)
    assert result is response


@pytest.mark.django_db
def test_assert_session_has_should_raise_when_key_absent_from_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="Session key 'missing' not found"):
        response.assert_session_has("missing")


@pytest.mark.django_db
def test_assert_session_has_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="expected '999'"):
        response.assert_session_has("user_id", 999)


@pytest.mark.django_db
def test_assert_session_missing_should_pass_when_key_absent_from_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_missing("nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_session_missing_should_raise_when_key_present_in_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_session_missing("user_id")


@pytest.mark.django_db
def test_assert_session_has_all_should_pass_when_every_key_present_in_session(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_has_all(["user_id", "username"])
    assert result is response


@pytest.mark.django_db
def test_assert_session_has_all_should_raise_when_any_key_absent_from_session(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="Session missing keys"):
        response.assert_session_has_all(["user_id", "nonexistent"])


@pytest.mark.django_db
def test_assert_session_should_raise_when_response_has_no_request_context(fluent_admin_client: FluentHttpAssertClient):
    response = FluentResponse(HttpResponse("test"))
    with pytest.raises(AssertionError, match="no request context"):
        response.assert_session_has("key")
