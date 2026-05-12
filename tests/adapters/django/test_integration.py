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


@pytest.mark.django_db
def test_assert_json_should_return_assertable_json_when_no_arguments(fluent_admin_client: FluentHttpAssertClient):
    from pyssertive.http.json import AssertableJson

    response = fluent_admin_client.get("/json/")
    result = response.assert_json()
    assert isinstance(result, AssertableJson)


@pytest.mark.django_db
def test_assert_json_should_raise_when_payload_is_invalid(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/invalid-json/")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.assert_json()


@pytest.mark.django_db
def test_assert_json_path_should_pass_when_value_matches_at_path(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_path("ok", True)
    assert result is response


@pytest.mark.django_db
def test_assert_json_path_should_resolve_nested_paths(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_path("items.0.id", 1)
    assert result is response


@pytest.mark.django_db
def test_assert_json_path_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected"):
        response.assert_json_path("ok", False)


@pytest.mark.django_db
def test_assert_json_path_should_raise_when_path_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_path("missing.path", True)


@pytest.mark.django_db
def test_assert_json_fragment_should_pass_when_fragment_is_subset(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_fragment({"ok": True})
    assert result is response


@pytest.mark.django_db
def test_assert_json_fragment_should_raise_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_fragment({"missing": "value"})


@pytest.mark.django_db
def test_assert_json_missing_fragment_should_pass_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_missing_fragment({"missing": "value"})
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_fragment_should_raise_when_fragment_present(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Unexpected fragment"):
        response.assert_json_missing_fragment({"ok": True})


@pytest.mark.django_db
def test_assert_json_count_should_pass_when_count_matches_at_path(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_count(3, path="items")
    assert result is response


@pytest.mark.django_db
def test_assert_json_count_should_apply_at_root_when_no_path_given(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    with pytest.raises(AssertionError, match="Expected 3 items"):
        response.assert_json_count(3)


@pytest.mark.django_db
def test_assert_json_count_should_raise_when_count_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    with pytest.raises(AssertionError, match="Expected 5 items"):
        response.assert_json_count(5, path="items")


@pytest.mark.django_db
def test_assert_json_count_should_raise_when_value_is_not_countable(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="countable"):
        response.assert_json_count(1, path="ok")


@pytest.mark.django_db
def test_assert_exact_json_should_pass_when_payload_matches_full_value(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_exact_json({"ok": True})
    assert result is response


@pytest.mark.django_db
def test_assert_exact_json_should_raise_when_payload_differs(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected exact JSON"):
        response.assert_exact_json({"ok": True, "extra": "field"})


@pytest.mark.django_db
def test_assert_json_structure_should_pass_when_keys_and_types_match(fluent_admin_client: FluentHttpAssertClient):
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
def test_assert_json_structure_should_raise_when_key_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Key 'missing' missing"):
        response.assert_json_structure({"missing": str})


@pytest.mark.django_db
def test_assert_json_structure_should_raise_when_type_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="expected type str"):
        response.assert_json_structure({"ok": str})


@pytest.mark.django_db
def test_assert_json_structure_should_raise_when_payload_is_not_dict(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        response.assert_json_structure({"key": str})


@pytest.mark.django_db
def test_assert_json_structure_should_only_check_key_presence_when_type_is_none(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_structure({"ok": None})
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_when_path_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_missing_path("missing.path")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_raise_when_path_exists(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_json_missing_path("ok")


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_for_nested_absent_path(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("user.nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_when_array_index_out_of_bounds(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("tags.99")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_when_segment_not_traversable(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("count.invalid")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_for_absent_path_through_array(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_missing_path("items.0.nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_list_should_pass_when_payload_is_list(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    result = response.assert_json_is_list()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_list_should_raise_when_payload_is_dict(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected JSON list"):
        response.assert_json_is_list()


@pytest.mark.django_db
def test_assert_json_is_dict_should_pass_when_payload_is_dict(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_is_dict()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_dict_should_raise_when_payload_is_list(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        response.assert_json_is_dict()


@pytest.mark.django_db
def test_assert_json_is_array_should_warn_as_deprecated_alias(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    with pytest.warns(DeprecationWarning, match="assert_json_is_array"):
        result = response.assert_json_is_array()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_object_should_warn_as_deprecated_alias(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.warns(DeprecationWarning, match="assert_json_is_object"):
        result = response.assert_json_is_object()
    assert result is response


@pytest.mark.django_db
def test_assert_json_should_return_response_when_path_and_callback_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json("user", lambda u: u.where("name", "John"))
    assert result is response


@pytest.mark.django_db
def test_assert_json_should_return_scoped_assertable_when_only_path_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    from pyssertive.http.json import AssertableJson

    response = fluent_admin_client.get("/json-nested/")
    scoped = response.assert_json("user")
    assert isinstance(scoped, AssertableJson)
    scoped.where("name", "John")


@pytest.mark.django_db
def test_assert_json_should_cache_parsed_payload_across_calls(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    first = response.assert_json()
    second = response.assert_json()
    assert first is second


@pytest.mark.django_db
def test_assert_json_should_not_mutate_cache_when_scoping(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-nested/")
    root_before = response.assert_json()
    response.assert_json("user", lambda u: u.where("name", "John"))
    root_after = response.assert_json()
    assert root_before is root_after


@pytest.mark.django_db
def test_assert_see_html_should_pass_when_text_present_in_markup(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_html("Hello World")
    assert result is response


@pytest.mark.django_db
def test_assert_see_html_should_match_html_markup_fragments(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_html("<strong>bold text</strong>")
    assert result is response


@pytest.mark.django_db
def test_assert_see_html_should_raise_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see HTML markup"):
        response.assert_see_html("Missing Text")


@pytest.mark.django_db
def test_assert_dont_see_html_should_pass_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_dont_see_html("Missing Text")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_html_should_raise_when_text_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Did not expect HTML markup"):
        response.assert_dont_see_html("Hello World")


@pytest.mark.django_db
def test_assert_see_text_should_pass_when_text_visible_in_rendered_output(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_text("bold text")
    assert result is response


@pytest.mark.django_db
def test_assert_see_text_should_not_match_html_tags(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        response.assert_see_text("<strong>")


@pytest.mark.django_db
def test_assert_see_text_should_raise_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        response.assert_see_text("Missing")


@pytest.mark.django_db
def test_assert_dont_see_text_should_pass_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_dont_see_text("Missing")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_text_should_raise_when_text_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Did not expect rendered text"):
        response.assert_dont_see_text("bold text")


@pytest.mark.django_db
def test_assert_see_html_in_order_should_pass_when_fragments_appear_in_sequence(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_html_in_order(["Hello", "<strong>bold"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_html_in_order_should_raise_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="HTML markup 'Missing'"):
        response.assert_see_html_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_see_html_in_order_should_raise_when_order_is_wrong(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="after 'test page'"):
        response.assert_see_html_in_order(["test page", "Hello"])


@pytest.mark.django_db
def test_assert_see_text_in_order_should_pass_when_texts_appear_in_sequence(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_text_in_order(["Hello", "bold text"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_text_in_order_should_raise_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Rendered text 'Missing'"):
        response.assert_see_text_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_see_text_in_order_should_raise_when_order_is_wrong(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="after 'bold text'"):
        response.assert_see_text_in_order(["bold text", "Hello"])


@pytest.mark.django_db
def test_assert_html_contains_should_pass_when_fragment_present_in_document(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    result = response.assert_html_contains("<h1>Hello World</h1>")
    assert result is response


@pytest.mark.django_db
def test_assert_html_contains_should_raise_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError):
        response.assert_html_contains("<h1>Missing</h1>")


@pytest.mark.django_db
def test_assert_see_should_warn_as_deprecated_alias_and_still_assert(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning, match="assert_see\\(\\) is deprecated"):
        result = response.assert_see("Hello World")
    assert result is response


@pytest.mark.django_db
def test_assert_see_should_warn_as_deprecated_alias_and_raise_when_absent(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning), pytest.raises(AssertionError, match="Expected to see HTML markup"):
        response.assert_see("Missing Text")


@pytest.mark.django_db
def test_assert_dont_see_should_warn_as_deprecated_alias_and_still_assert(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning, match="assert_dont_see\\(\\) is deprecated"):
        result = response.assert_dont_see("Missing Text")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_should_warn_as_deprecated_alias_and_raise_when_present(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning), pytest.raises(AssertionError, match="Did not expect HTML markup"):
        response.assert_dont_see("Hello World")


@pytest.mark.django_db
def test_assert_see_in_order_should_warn_as_deprecated_alias_and_still_assert(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning, match="assert_see_in_order\\(\\) is deprecated"):
        result = response.assert_see_in_order(["Hello", "test page"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_in_order_should_warn_as_deprecated_alias_and_raise_when_fragment_absent(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning), pytest.raises(AssertionError, match="not found"):
        response.assert_see_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_html_should_return_response_when_selector_and_callback_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html-sections/")
    result = response.assert_html(
        "table#active-users",
        lambda users: users.count("tbody tr", 3).see_text("Alice"),
    )
    assert result is response


@pytest.mark.django_db
def test_assert_html_should_return_document_assertable_when_no_arguments(fluent_admin_client: FluentHttpAssertClient):
    from pyssertive.http.html import AssertableHtml

    response = fluent_admin_client.get("/html-sections/")
    doc = response.assert_html()
    assert isinstance(doc, AssertableHtml)


@pytest.mark.django_db
def test_assert_html_should_return_scoped_assertable_when_only_selector_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    from pyssertive.http.html import AssertableHtml

    response = fluent_admin_client.get("/html-sections/")
    table = response.assert_html("table#active-users")
    assert isinstance(table, AssertableHtml)
    table.count("tbody tr", 3)


@pytest.mark.django_db
def test_assert_html_should_raise_when_selector_does_not_match(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    with pytest.raises(AssertionError, match="Selector 'table#nonexistent' not found"):
        response.assert_html("table#nonexistent", lambda _: None)


@pytest.mark.django_db
def test_assert_html_should_isolate_assertions_to_scoped_section(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    result = (
        response.assert_ok()
        .assert_html("section#billing", lambda s: s.see_text("alice@example.com"))
        .assert_html("section#audit-log", lambda s: s.dont_see_text("alice@example.com").see_text("bob@example.com"))
    )
    assert result is response


@pytest.mark.django_db
def test_assert_html_should_cache_parsed_document_across_calls(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    first = response.assert_html()
    second = response.assert_html()
    assert first is second


@pytest.mark.django_db
def test_assert_html_should_not_contaminate_cache_when_alternating_root_and_scoped_calls(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html-sections/")
    result = (
        response.assert_ok()
        .assert_see_text("Dashboard")
        .assert_html("table#active-users", lambda t: t.count("tbody tr.row", 3).see_text("Alice"))
        .assert_html("section#billing", lambda s: s.see_text("alice@example.com").dont_see_text("Carol"))
        .assert_html("section#audit-log", lambda s: s.see_text("bob@example.com").dont_see_text("Alice"))
        .assert_see_text("Footer text outside the table")
    )
    assert result is response


@pytest.mark.django_db
def test_assert_html_should_not_mutate_cached_root_when_scoping(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    root_before = response.assert_html()
    response.assert_html("table#active-users", lambda t: t.count("tbody tr.row", 3))
    root_after = response.assert_html()
    assert root_before is root_after
    response.assert_see_text("Dashboard").assert_see_text("Footer text outside the table")


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
