import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_cookie_should_pass_when_cookie_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.assert_cookie("session_id")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_should_pass_when_value_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.assert_cookie("session_id", "abc123")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_should_raise_when_cookie_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
        response.assert_cookie("missing")


@pytest.mark.django_db
def test_assert_cookie_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="expected 'wrong'"):
        response.assert_cookie("session_id", "wrong")


@pytest.mark.django_db
def test_assert_cookie_missing_should_pass_when_cookie_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.assert_cookie_missing("nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_missing_should_raise_when_cookie_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_cookie_missing("session_id")


@pytest.mark.django_db
def test_assert_cookie_expired_should_pass_when_cookie_expired(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-expire/")
    result = response.assert_cookie_expired("session_id")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_expired_should_raise_when_cookie_still_active(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="is not expired"):
        response.assert_cookie_expired("session_id")


@pytest.mark.django_db
def test_assert_cookie_expired_should_raise_when_cookie_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_cookie_expired("missing")
