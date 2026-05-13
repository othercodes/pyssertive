from __future__ import annotations

import pytest

from tests.adapters._factories import RESPONSE_FACTORIES

STATUS_HELPERS = [
    ("assert_ok", 200, 404, "Expected 2xx"),
    ("assert_created", 201, 200, "Expected 201"),
    ("assert_accepted", 202, 200, "Expected 202"),
    ("assert_no_content", 204, 200, "Expected 204"),
    ("assert_redirect", 302, 200, "Expected redirect"),
    ("assert_moved_permanently", 301, 200, "Expected 301"),
    ("assert_found", 302, 200, "Expected 302"),
    ("assert_see_other", 303, 200, "Expected 303"),
    ("assert_bad_request", 400, 200, "Expected 400"),
    ("assert_payment_required", 402, 200, "Expected 402"),
    ("assert_unauthorized", 401, 200, "Expected 401"),
    ("assert_forbidden", 403, 200, "Expected 403"),
    ("assert_not_found", 404, 200, "Expected 404"),
    ("assert_method_not_allowed", 405, 200, "Expected 405"),
    ("assert_request_timeout", 408, 200, "Expected 408"),
    ("assert_conflict", 409, 200, "Expected 409"),
    ("assert_gone", 410, 200, "Expected 410"),
    ("assert_unprocessable", 422, 200, "Expected 422"),
    ("assert_too_many_requests", 429, 200, "Expected 429"),
    ("assert_internal_server_error", 500, 200, "Expected 500"),
    ("assert_service_unavailable", 503, 200, "Expected 503"),
    ("assert_server_error", 500, 200, "Expected 5xx"),
    ("assert_client_error", 400, 200, "Expected 4xx"),
]


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
@pytest.mark.parametrize(("method", "success_status", "fail_status", "error_match"), STATUS_HELPERS)
def test_status_assertion_should_pass_when_status_matches(
    make_response, method, success_status, fail_status, error_match
):
    response = make_response(status=success_status)
    result = getattr(response, method)()
    assert result is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
@pytest.mark.parametrize(("method", "success_status", "fail_status", "error_match"), STATUS_HELPERS)
def test_status_assertion_should_raise_when_status_mismatches(
    make_response, method, success_status, fail_status, error_match
):
    response = make_response(status=fail_status)
    with pytest.raises(AssertionError, match=error_match):
        getattr(response, method)()


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_redirect_should_pass_when_target_matches(make_response):
    response = make_response(status=302, headers={"Location": "/json/"})
    assert response.assert_redirect(to="/json/") is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_redirect_should_raise_when_target_mismatches(make_response):
    response = make_response(status=302, headers={"Location": "/json/"})
    with pytest.raises(AssertionError, match="Expected redirect to"):
        response.assert_redirect(to="/wrong/")


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_status_should_pass_when_status_code_matches(make_response):
    response = make_response(status=200)
    assert response.assert_status(200) is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_assert_status_should_raise_when_status_code_mismatches(make_response):
    response = make_response(status=200)
    with pytest.raises(AssertionError, match="Expected status 201"):
        response.assert_status(201)
