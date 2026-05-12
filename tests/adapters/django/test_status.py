import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_ok_should_pass_when_status_is_2xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_ok()
    assert result is response


@pytest.mark.django_db
def test_assert_ok_should_raise_when_status_is_not_2xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/not-found/")
    with pytest.raises(AssertionError, match="Expected 2xx"):
        response.assert_ok()


@pytest.mark.django_db
def test_assert_created_should_pass_when_status_is_201(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/created/")
    result = response.assert_created()
    assert result is response


@pytest.mark.django_db
def test_assert_created_should_raise_when_status_is_not_201(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 201"):
        response.assert_created()


@pytest.mark.django_db
def test_assert_accepted_should_pass_when_status_is_202(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/accepted/")
    result = response.assert_accepted()
    assert result is response


@pytest.mark.django_db
def test_assert_accepted_should_raise_when_status_is_not_202(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 202"):
        response.assert_accepted()


@pytest.mark.django_db
def test_assert_no_content_should_pass_when_status_is_204(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/no-content/")
    result = response.assert_no_content()
    assert result is response


@pytest.mark.django_db
def test_assert_no_content_should_raise_when_status_is_not_204(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 204"):
        response.assert_no_content()


@pytest.mark.django_db
def test_assert_redirect_should_pass_when_status_is_3xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/redirect/")
    result = response.assert_redirect()
    assert result is response


@pytest.mark.django_db
def test_assert_redirect_should_pass_when_target_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/redirect/")
    result = response.assert_redirect(to="/json/")
    assert result is response


@pytest.mark.django_db
def test_assert_redirect_should_raise_when_target_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/redirect/")
    with pytest.raises(AssertionError, match="Expected redirect to"):
        response.assert_redirect(to="/wrong/")


@pytest.mark.django_db
def test_assert_redirect_should_raise_when_status_is_not_3xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected redirect"):
        response.assert_redirect()


@pytest.mark.django_db
def test_assert_moved_permanently_should_pass_when_status_is_301(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/moved-permanently/")
    result = response.assert_moved_permanently()
    assert result is response


@pytest.mark.django_db
def test_assert_moved_permanently_should_raise_when_status_is_not_301(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 301"):
        response.assert_moved_permanently()


@pytest.mark.django_db
def test_assert_found_should_pass_when_status_is_302(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/found/")
    result = response.assert_found()
    assert result is response


@pytest.mark.django_db
def test_assert_found_should_raise_when_status_is_not_302(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 302"):
        response.assert_found()


@pytest.mark.django_db
def test_assert_see_other_should_pass_when_status_is_303(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/see-other/")
    result = response.assert_see_other()
    assert result is response


@pytest.mark.django_db
def test_assert_see_other_should_raise_when_status_is_not_303(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 303"):
        response.assert_see_other()


@pytest.mark.django_db
def test_assert_bad_request_should_pass_when_status_is_400(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/bad-request/")
    result = response.assert_bad_request()
    assert result is response


@pytest.mark.django_db
def test_assert_bad_request_should_raise_when_status_is_not_400(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 400"):
        response.assert_bad_request()


@pytest.mark.django_db
def test_assert_unauthorized_should_pass_when_status_is_401(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/unauthorized/")
    result = response.assert_unauthorized()
    assert result is response


@pytest.mark.django_db
def test_assert_unauthorized_should_raise_when_status_is_not_401(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 401"):
        response.assert_unauthorized()


@pytest.mark.django_db
def test_assert_forbidden_should_pass_when_status_is_403(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/forbidden/")
    result = response.assert_forbidden()
    assert result is response


@pytest.mark.django_db
def test_assert_forbidden_should_raise_when_status_is_not_403(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 403"):
        response.assert_forbidden()


@pytest.mark.django_db
def test_assert_not_found_should_pass_when_status_is_404(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/not-found/")
    result = response.assert_not_found()
    assert result is response


@pytest.mark.django_db
def test_assert_not_found_should_raise_when_status_is_not_404(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 404"):
        response.assert_not_found()


@pytest.mark.django_db
def test_assert_conflict_should_pass_when_status_is_409(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/conflict/")
    result = response.assert_conflict()
    assert result is response


@pytest.mark.django_db
def test_assert_conflict_should_raise_when_status_is_not_409(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 409"):
        response.assert_conflict()


@pytest.mark.django_db
def test_assert_gone_should_pass_when_status_is_410(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/gone/")
    result = response.assert_gone()
    assert result is response


@pytest.mark.django_db
def test_assert_gone_should_raise_when_status_is_not_410(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 410"):
        response.assert_gone()


@pytest.mark.django_db
def test_assert_unprocessable_should_pass_when_status_is_422(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/unprocessable/")
    result = response.assert_unprocessable()
    assert result is response


@pytest.mark.django_db
def test_assert_unprocessable_should_raise_when_status_is_not_422(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 422"):
        response.assert_unprocessable()


@pytest.mark.django_db
def test_assert_too_many_requests_should_pass_when_status_is_429(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/too-many-requests/")
    result = response.assert_too_many_requests()
    assert result is response


@pytest.mark.django_db
def test_assert_too_many_requests_should_raise_when_status_is_not_429(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 429"):
        response.assert_too_many_requests()


@pytest.mark.django_db
def test_assert_server_error_should_pass_when_status_is_5xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/server-error/")
    result = response.assert_server_error()
    assert result is response


@pytest.mark.django_db
def test_assert_server_error_should_raise_when_status_is_not_5xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 5xx"):
        response.assert_server_error()


@pytest.mark.django_db
def test_assert_status_should_pass_when_status_code_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_status(200)
    assert result is response


@pytest.mark.django_db
def test_assert_status_should_raise_when_status_code_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected status 201"):
        response.assert_status(201)


@pytest.mark.django_db
def test_assert_payment_required_should_pass_when_status_is_402(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/payment-required/")
    result = response.assert_payment_required()
    assert result is response


@pytest.mark.django_db
def test_assert_payment_required_should_raise_when_status_is_not_402(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 402"):
        response.assert_payment_required()


@pytest.mark.django_db
def test_assert_method_not_allowed_should_pass_when_status_is_405(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/method-not-allowed/")
    result = response.assert_method_not_allowed()
    assert result is response


@pytest.mark.django_db
def test_assert_method_not_allowed_should_raise_when_status_is_not_405(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 405"):
        response.assert_method_not_allowed()


@pytest.mark.django_db
def test_assert_request_timeout_should_pass_when_status_is_408(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/request-timeout/")
    result = response.assert_request_timeout()
    assert result is response


@pytest.mark.django_db
def test_assert_request_timeout_should_raise_when_status_is_not_408(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 408"):
        response.assert_request_timeout()


@pytest.mark.django_db
def test_assert_internal_server_error_should_pass_when_status_is_500(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/server-error/")
    result = response.assert_internal_server_error()
    assert result is response


@pytest.mark.django_db
def test_assert_internal_server_error_should_raise_when_status_is_not_500(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 500"):
        response.assert_internal_server_error()


@pytest.mark.django_db
def test_assert_service_unavailable_should_pass_when_status_is_503(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/service-unavailable/")
    result = response.assert_service_unavailable()
    assert result is response


@pytest.mark.django_db
def test_assert_service_unavailable_should_raise_when_status_is_not_503(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 503"):
        response.assert_service_unavailable()


@pytest.mark.django_db
def test_assert_client_error_should_pass_when_status_is_4xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/bad-request/")
    result = response.assert_client_error()
    assert result is response


@pytest.mark.django_db
def test_assert_client_error_should_raise_when_status_is_not_4xx(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 4xx"):
        response.assert_client_error()
