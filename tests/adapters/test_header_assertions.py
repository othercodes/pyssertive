from __future__ import annotations

import pytest

from tests.adapters._factories import RESPONSE_FACTORIES

CUSTOM_HEADERS = {
    "X-Custom-Header": "custom-value",
    "X-Another-Header": "value-with-fragment-inside",
    "Content-Type": "application/json",
}


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_should_pass_when_value_matches(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    assert response.assert_header("X-Custom-Header", "custom-value") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_should_raise_when_value_mismatches(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    with pytest.raises(AssertionError, match="Expected header"):
        response.assert_header("X-Custom-Header", "wrong")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_contains_should_pass_when_fragment_present(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    assert response.assert_header_contains("X-Another-Header", "fragment") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_contains_should_raise_when_header_absent(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    with pytest.raises(AssertionError, match=r"Expected header .* to exist"):
        response.assert_header_contains("X-Missing-Header", "fragment")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_contains_should_raise_when_fragment_absent_from_value(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    with pytest.raises(AssertionError, match="to contain"):
        response.assert_header_contains("X-Custom-Header", "missing")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_missing_should_pass_when_header_absent(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    assert response.assert_header_missing("X-Nonexistent") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_header_missing_should_raise_when_header_present(make_response):
    response = make_response(headers=CUSTOM_HEADERS)
    with pytest.raises(AssertionError, match="to be missing"):
        response.assert_header_missing("X-Custom-Header")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_content_type_should_pass_when_value_matches(make_response):
    response = make_response(headers={"Content-Type": "application/json"})
    assert response.assert_content_type("application/json") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_content_type_should_raise_when_value_mismatches(make_response):
    response = make_response(headers={"Content-Type": "application/json"})
    with pytest.raises(AssertionError, match="Expected Content-Type"):
        response.assert_content_type("text/html")
