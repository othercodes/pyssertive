from __future__ import annotations

import pytest

from tests.adapters._factories import RESPONSE_FACTORIES

COOKIES = {
    "session_id": {"value": "abc123"},
    "tracking": {"value": "xyz"},
}

EXPIRED_COOKIES = {
    "session_id": {"value": "abc123", "max_age": 0},
}


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_should_pass_when_cookie_present(make_response):
    response = make_response(cookies=COOKIES)
    assert response.assert_cookie("session_id") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_should_pass_when_value_matches(make_response):
    response = make_response(cookies=COOKIES)
    assert response.assert_cookie("session_id", "abc123") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_should_raise_when_cookie_absent(make_response):
    response = make_response(cookies=COOKIES)
    with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
        response.assert_cookie("missing")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_should_raise_when_value_mismatches(make_response):
    response = make_response(cookies=COOKIES)
    with pytest.raises(AssertionError, match="expected 'wrong'"):
        response.assert_cookie("session_id", "wrong")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_missing_should_pass_when_cookie_absent(make_response):
    response = make_response(cookies=COOKIES)
    assert response.assert_cookie_missing("nonexistent") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_missing_should_raise_when_cookie_present(make_response):
    response = make_response(cookies=COOKIES)
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_cookie_missing("session_id")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_expired_should_pass_when_cookie_expired(make_response):
    response = make_response(cookies=EXPIRED_COOKIES)
    assert response.assert_cookie_expired("session_id") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_expired_should_raise_when_cookie_still_active(make_response):
    response = make_response(cookies=COOKIES)
    with pytest.raises(AssertionError, match="is not expired"):
        response.assert_cookie_expired("session_id")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_cookie_expired_should_raise_when_cookie_absent(make_response):
    response = make_response(cookies=COOKIES)
    with pytest.raises(AssertionError, match="not found"):
        response.assert_cookie_expired("missing")
