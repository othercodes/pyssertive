import pytest


@pytest.mark.django_db
def test_assert_ok(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_ok()
    assert result is response


@pytest.mark.django_db
def test_assert_ok_fails_for_non_2xx(fluent_admin_client):
    response = fluent_admin_client.get("/not-found/")
    with pytest.raises(AssertionError, match="Expected 2xx"):
        response.assert_ok()


@pytest.mark.django_db
def test_assert_created(fluent_admin_client):
    response = fluent_admin_client.get("/created/")
    result = response.assert_created()
    assert result is response


@pytest.mark.django_db
def test_assert_created_fails_for_non_201(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 201"):
        response.assert_created()


@pytest.mark.django_db
def test_assert_accepted(fluent_admin_client):
    response = fluent_admin_client.get("/accepted/")
    result = response.assert_accepted()
    assert result is response


@pytest.mark.django_db
def test_assert_accepted_fails_for_non_202(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 202"):
        response.assert_accepted()


@pytest.mark.django_db
def test_assert_no_content(fluent_admin_client):
    response = fluent_admin_client.get("/no-content/")
    result = response.assert_no_content()
    assert result is response


@pytest.mark.django_db
def test_assert_no_content_fails_for_non_204(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 204"):
        response.assert_no_content()


@pytest.mark.django_db
def test_assert_redirect(fluent_admin_client):
    response = fluent_admin_client.get("/redirect/")
    result = response.assert_redirect()
    assert result is response


@pytest.mark.django_db
def test_assert_redirect_with_target(fluent_admin_client):
    response = fluent_admin_client.get("/redirect/")
    result = response.assert_redirect(to="/json/")
    assert result is response


@pytest.mark.django_db
def test_assert_redirect_fails_with_wrong_target(fluent_admin_client):
    response = fluent_admin_client.get("/redirect/")
    with pytest.raises(AssertionError, match="Expected redirect to"):
        response.assert_redirect(to="/wrong/")


@pytest.mark.django_db
def test_assert_redirect_fails_for_non_3xx(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected redirect"):
        response.assert_redirect()


@pytest.mark.django_db
def test_assert_moved_permanently(fluent_admin_client):
    response = fluent_admin_client.get("/moved-permanently/")
    result = response.assert_moved_permanently()
    assert result is response


@pytest.mark.django_db
def test_assert_moved_permanently_fails_for_non_301(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 301"):
        response.assert_moved_permanently()


@pytest.mark.django_db
def test_assert_found(fluent_admin_client):
    response = fluent_admin_client.get("/found/")
    result = response.assert_found()
    assert result is response


@pytest.mark.django_db
def test_assert_found_fails_for_non_302(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 302"):
        response.assert_found()


@pytest.mark.django_db
def test_assert_see_other(fluent_admin_client):
    response = fluent_admin_client.get("/see-other/")
    result = response.assert_see_other()
    assert result is response


@pytest.mark.django_db
def test_assert_see_other_fails_for_non_303(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 303"):
        response.assert_see_other()


@pytest.mark.django_db
def test_assert_bad_request(fluent_admin_client):
    response = fluent_admin_client.get("/bad-request/")
    result = response.assert_bad_request()
    assert result is response


@pytest.mark.django_db
def test_assert_bad_request_fails_for_non_400(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 400"):
        response.assert_bad_request()


@pytest.mark.django_db
def test_assert_unauthorized(fluent_admin_client):
    response = fluent_admin_client.get("/unauthorized/")
    result = response.assert_unauthorized()
    assert result is response


@pytest.mark.django_db
def test_assert_unauthorized_fails_for_non_401(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 401"):
        response.assert_unauthorized()


@pytest.mark.django_db
def test_assert_forbidden(fluent_admin_client):
    response = fluent_admin_client.get("/forbidden/")
    result = response.assert_forbidden()
    assert result is response


@pytest.mark.django_db
def test_assert_forbidden_fails_for_non_403(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 403"):
        response.assert_forbidden()


@pytest.mark.django_db
def test_assert_not_found(fluent_admin_client):
    response = fluent_admin_client.get("/not-found/")
    result = response.assert_not_found()
    assert result is response


@pytest.mark.django_db
def test_assert_not_found_fails_for_non_404(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 404"):
        response.assert_not_found()


@pytest.mark.django_db
def test_assert_conflict(fluent_admin_client):
    response = fluent_admin_client.get("/conflict/")
    result = response.assert_conflict()
    assert result is response


@pytest.mark.django_db
def test_assert_conflict_fails_for_non_409(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 409"):
        response.assert_conflict()


@pytest.mark.django_db
def test_assert_gone(fluent_admin_client):
    response = fluent_admin_client.get("/gone/")
    result = response.assert_gone()
    assert result is response


@pytest.mark.django_db
def test_assert_gone_fails_for_non_410(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 410"):
        response.assert_gone()


@pytest.mark.django_db
def test_assert_unprocessable(fluent_admin_client):
    response = fluent_admin_client.get("/unprocessable/")
    result = response.assert_unprocessable()
    assert result is response


@pytest.mark.django_db
def test_assert_unprocessable_fails_for_non_422(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 422"):
        response.assert_unprocessable()


@pytest.mark.django_db
def test_assert_too_many_requests(fluent_admin_client):
    response = fluent_admin_client.get("/too-many-requests/")
    result = response.assert_too_many_requests()
    assert result is response


@pytest.mark.django_db
def test_assert_too_many_requests_fails_for_non_429(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 429"):
        response.assert_too_many_requests()


@pytest.mark.django_db
def test_assert_server_error(fluent_admin_client):
    response = fluent_admin_client.get("/server-error/")
    result = response.assert_server_error()
    assert result is response


@pytest.mark.django_db
def test_assert_server_error_fails_for_non_5xx(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 5xx"):
        response.assert_server_error()


@pytest.mark.django_db
def test_assert_status(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_status(200)
    assert result is response


@pytest.mark.django_db
def test_assert_status_fails_for_wrong_code(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected status 201"):
        response.assert_status(201)


@pytest.mark.django_db
def test_assert_payment_required(fluent_admin_client):
    response = fluent_admin_client.get("/payment-required/")
    result = response.assert_payment_required()
    assert result is response


@pytest.mark.django_db
def test_assert_payment_required_fails_for_non_402(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 402"):
        response.assert_payment_required()


@pytest.mark.django_db
def test_assert_method_not_allowed(fluent_admin_client):
    response = fluent_admin_client.get("/method-not-allowed/")
    result = response.assert_method_not_allowed()
    assert result is response


@pytest.mark.django_db
def test_assert_method_not_allowed_fails_for_non_405(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 405"):
        response.assert_method_not_allowed()


@pytest.mark.django_db
def test_assert_request_timeout(fluent_admin_client):
    response = fluent_admin_client.get("/request-timeout/")
    result = response.assert_request_timeout()
    assert result is response


@pytest.mark.django_db
def test_assert_request_timeout_fails_for_non_408(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 408"):
        response.assert_request_timeout()


@pytest.mark.django_db
def test_assert_internal_server_error(fluent_admin_client):
    response = fluent_admin_client.get("/server-error/")
    result = response.assert_internal_server_error()
    assert result is response


@pytest.mark.django_db
def test_assert_internal_server_error_fails_for_non_500(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 500"):
        response.assert_internal_server_error()


@pytest.mark.django_db
def test_assert_service_unavailable(fluent_admin_client):
    response = fluent_admin_client.get("/service-unavailable/")
    result = response.assert_service_unavailable()
    assert result is response


@pytest.mark.django_db
def test_assert_service_unavailable_fails_for_non_503(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 503"):
        response.assert_service_unavailable()


@pytest.mark.django_db
def test_assert_client_error(fluent_admin_client):
    response = fluent_admin_client.get("/bad-request/")
    result = response.assert_client_error()
    assert result is response


@pytest.mark.django_db
def test_assert_client_error_fails_for_non_4xx(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected 4xx"):
        response.assert_client_error()


@pytest.mark.django_db
def test_assert_header(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.assert_header("X-Custom-Header", "custom-value")
    assert result is response


@pytest.mark.django_db
def test_assert_header_fails_for_wrong_value(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match="Expected header"):
        response.assert_header("X-Custom-Header", "wrong-value")


@pytest.mark.django_db
def test_assert_header_contains(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.assert_header_contains("X-Another-Header", "fragment")
    assert result is response


@pytest.mark.django_db
def test_assert_header_contains_fails_for_missing_header(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match=r"Expected header .* to exist"):
        response.assert_header_contains("X-Missing-Header", "fragment")


@pytest.mark.django_db
def test_assert_header_contains_fails_for_missing_fragment(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match="to contain"):
        response.assert_header_contains("X-Custom-Header", "missing")


@pytest.mark.django_db
def test_assert_header_missing(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.assert_header_missing("X-Nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_header_missing_fails_when_present(fluent_admin_client):
    response = fluent_admin_client.get("/custom-headers/")
    with pytest.raises(AssertionError, match="to be missing"):
        response.assert_header_missing("X-Custom-Header")


@pytest.mark.django_db
def test_assert_content_type(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_content_type("application/json")
    assert result is response


@pytest.mark.django_db
def test_assert_content_type_fails_for_wrong_type(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected Content-Type"):
        response.assert_content_type("text/html")


@pytest.mark.django_db
def test_assert_json(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json()
    assert result is response


@pytest.mark.django_db
def test_assert_json_fails_for_invalid_json(fluent_admin_client):
    response = fluent_admin_client.get("/invalid-json/")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.assert_json()


@pytest.mark.django_db
def test_assert_json_path(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_path("ok", True)
    assert result is response


@pytest.mark.django_db
def test_assert_json_path_nested(fluent_admin_client):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_path("items.0.id", 1)
    assert result is response


@pytest.mark.django_db
def test_assert_json_path_fails_for_wrong_value(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected"):
        response.assert_json_path("ok", False)


@pytest.mark.django_db
def test_assert_json_path_fails_for_missing_path(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_path("missing.path", True)


@pytest.mark.django_db
def test_assert_json_fragment(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_fragment({"ok": True})
    assert result is response


@pytest.mark.django_db
def test_assert_json_fragment_fails_for_missing(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_fragment({"missing": "value"})


@pytest.mark.django_db
def test_assert_json_missing_fragment(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_missing_fragment({"missing": "value"})
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_fragment_fails_when_present(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Unexpected fragment"):
        response.assert_json_missing_fragment({"ok": True})


@pytest.mark.django_db
def test_assert_json_count_with_path(fluent_admin_client):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_count(3, path="items")
    assert result is response


@pytest.mark.django_db
def test_assert_json_count_without_path(fluent_admin_client):
    response = fluent_admin_client.get("/json-list/")
    with pytest.raises(AssertionError, match="Expected a list"):
        response.assert_json_count(3)


@pytest.mark.django_db
def test_assert_json_count_fails_for_wrong_count(fluent_admin_client):
    response = fluent_admin_client.get("/json-list/")
    with pytest.raises(AssertionError, match="Expected 5 items"):
        response.assert_json_count(5, path="items")


@pytest.mark.django_db
def test_assert_json_count_fails_for_non_list(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected a list"):
        response.assert_json_count(1, path="ok")


@pytest.mark.django_db
def test_assert_exact_json(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_exact_json({"ok": True})
    assert result is response


@pytest.mark.django_db
def test_assert_exact_json_fails_for_mismatch(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected exact JSON"):
        response.assert_exact_json({"ok": True, "extra": "field"})


@pytest.mark.django_db
def test_assert_json_structure(fluent_admin_client):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_structure(
        {
            "user": dict,
            "tags": list,
            "count": int,
        }
    )
    assert result is response


@pytest.mark.django_db
def test_assert_json_structure_fails_for_missing_key(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Key 'missing' missing"):
        response.assert_json_structure({"missing": str})


@pytest.mark.django_db
def test_assert_json_structure_fails_for_wrong_type(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="expected type str"):
        response.assert_json_structure({"ok": str})


@pytest.mark.django_db
def test_assert_json_structure_fails_for_non_object(fluent_admin_client):
    response = fluent_admin_client.get("/json-array/")
    with pytest.raises(AssertionError, match="Expected JSON object"):
        response.assert_json_structure({"key": str})


@pytest.mark.django_db
def test_assert_json_structure_with_none_type(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_structure({"ok": None})
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_missing_path("missing.path")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_fails_when_exists(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_json_missing_path("ok")


@pytest.mark.django_db
def test_assert_json_missing_path_nested(fluent_admin_client):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("user.nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_array_index_out_of_bounds(fluent_admin_client):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("tags.99")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_invalid_path_segment(fluent_admin_client):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("count.invalid")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_through_array(fluent_admin_client):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_missing_path("items.0.nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_array(fluent_admin_client):
    response = fluent_admin_client.get("/json-array/")
    result = response.assert_json_is_array()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_array_fails_for_object(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected JSON array"):
        response.assert_json_is_array()


@pytest.mark.django_db
def test_assert_json_is_object(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_is_object()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_object_fails_for_array(fluent_admin_client):
    response = fluent_admin_client.get("/json-array/")
    with pytest.raises(AssertionError, match="Expected JSON object"):
        response.assert_json_is_object()


@pytest.mark.django_db
def test_assert_see(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see("Hello World")
    assert result is response


@pytest.mark.django_db
def test_assert_see_fails_for_missing_text(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see"):
        response.assert_see("Missing Text")


@pytest.mark.django_db
def test_assert_dont_see(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    result = response.assert_dont_see("Missing Text")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_fails_when_present(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Did not expect"):
        response.assert_dont_see("Hello World")


@pytest.mark.django_db
def test_assert_see_text(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_text("bold text")
    assert result is response


@pytest.mark.django_db
def test_assert_see_text_fails_for_missing(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see plain text"):
        response.assert_see_text("Missing")


@pytest.mark.django_db
def test_assert_dont_see_text(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    result = response.assert_dont_see_text("Missing")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_text_fails_when_present(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Did not expect plain text"):
        response.assert_dont_see_text("bold text")


@pytest.mark.django_db
def test_assert_see_in_order(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_in_order(["Hello", "test page"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_in_order_fails_for_missing(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_see_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_see_in_order_fails_for_wrong_order(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_see_in_order(["test page", "Hello"])


@pytest.mark.django_db
def test_assert_html_contains(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    result = response.assert_html_contains("<h1>Hello World</h1>")
    assert result is response


@pytest.mark.django_db
def test_assert_html_contains_fails_for_missing(fluent_admin_client):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError):
        response.assert_html_contains("<h1>Missing</h1>")


@pytest.mark.django_db
def test_assert_cookie(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.assert_cookie("session_id")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_with_value(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.assert_cookie("session_id", "abc123")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_fails_for_missing(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="Cookie 'missing' not found"):
        response.assert_cookie("missing")


@pytest.mark.django_db
def test_assert_cookie_fails_for_wrong_value(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="expected 'wrong'"):
        response.assert_cookie("session_id", "wrong")


@pytest.mark.django_db
def test_assert_cookie_missing(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.assert_cookie_missing("nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_missing_fails_when_present(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_cookie_missing("session_id")


@pytest.mark.django_db
def test_assert_cookie_expired(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-expire/")
    result = response.assert_cookie_expired("session_id")
    assert result is response


@pytest.mark.django_db
def test_assert_cookie_expired_fails_for_active_cookie(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="is not expired"):
        response.assert_cookie_expired("session_id")


@pytest.mark.django_db
def test_assert_cookie_expired_fails_for_missing(fluent_admin_client):
    response = fluent_admin_client.get("/cookie-set/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_cookie_expired("missing")
