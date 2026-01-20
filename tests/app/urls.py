from django.urls import path

from tests.app import views

urlpatterns = [
    # JSON endpoints
    path("json/", views.sample_json_view),
    path("json-list/", views.json_list_view),
    path("invalid-json/", views.invalid_json_view),
    # HTML endpoints
    path("html/", views.html_view),
    path("plain-text/", views.plain_text_view),
    # Status code endpoints
    path("created/", views.created_view),
    path("accepted/", views.accepted_view),
    path("no-content/", views.no_content_view),
    path("redirect/", views.redirect_view),
    path("moved-permanently/", views.moved_permanently_view),
    path("found/", views.found_view),
    path("see-other/", views.see_other_view),
    path("bad-request/", views.bad_request_view),
    path("unauthorized/", views.unauthorized_view),
    path("forbidden/", views.forbidden_view),
    path("not-found/", views.not_found_view),
    path("conflict/", views.conflict_view),
    path("gone/", views.gone_view),
    path("unprocessable/", views.unprocessable_view),
    path("too-many-requests/", views.too_many_requests_view),
    path("server-error/", views.server_error_view),
    # Header endpoints
    path("custom-headers/", views.custom_header_view),
    # Template endpoints
    path("template/", views.template_view),
    path("form-error/", views.form_error_view),
    path("formset-error/", views.formset_error_view),
    # Phase 2: New status codes
    path("payment-required/", views.payment_required_view),
    path("method-not-allowed/", views.method_not_allowed_view),
    path("request-timeout/", views.request_timeout_view),
    path("service-unavailable/", views.service_unavailable_view),
    # Phase 2: JSON structure
    path("json-array/", views.json_array_view),
    path("json-nested/", views.json_nested_view),
    # Phase 2: Session and cookies
    path("session-set/", views.session_set_view),
    path("cookie-set/", views.cookie_set_view),
    path("cookie-expire/", views.cookie_expire_view),
    path("cookie-detailed/", views.cookie_detailed_view),
    # Streaming and download endpoints
    path("streaming-csv/", views.streaming_csv_view),
    path("streaming-text/", views.streaming_text_view),
    path("streaming-empty/", views.streaming_empty_view),
    path("download/", views.download_view),
    path("inline/", views.inline_view),
]
