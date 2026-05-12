import pytest
from django.http import HttpResponse
from django.test import Client

from pyssertive.adapters.django import FluentHttpAssertClient, FluentResponse


@pytest.mark.django_db
def test_dump_should_pretty_print_json_when_content_type_is_json(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Dump" in captured.out
    assert "200" in captured.out


@pytest.mark.django_db
def test_dump_should_print_body_when_content_type_is_plain_text(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/plain-text/")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "Plain text content" in captured.out


@pytest.mark.django_db
def test_dump_should_use_explicit_content_format_when_provided(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump(content_format="text/plain")
    assert result is response
    captured = capsys.readouterr()
    assert "text/plain" in captured.out


@pytest.mark.django_db
def test_dump_should_report_invalid_json_when_payload_cannot_be_parsed(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/invalid-json/")
    result = response.dump(content_format="application/json")
    assert result is response
    captured = capsys.readouterr()
    assert "[Invalid JSON]" in captured.out


@pytest.mark.django_db
def test_dump_should_print_raw_body_when_content_type_is_unknown(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/html/")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Dump" in captured.out


@pytest.mark.django_db
def test_dump_headers_should_print_all_response_headers(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.dump_headers()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Headers]" in captured.out
    assert "X-Custom-Header" in captured.out


@pytest.mark.django_db
def test_dump_json_should_pretty_print_payload_when_valid(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump_json()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response JSON]" in captured.out
    assert '"ok": true' in captured.out


@pytest.mark.django_db
def test_dump_json_should_raise_when_payload_is_invalid(fluent_admin_client):
    response = fluent_admin_client.get("/invalid-json/")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.dump_json()


@pytest.mark.django_db
def test_dump_session_should_print_session_entries_when_session_populated(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/session-set/")
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "[Session Data]" in captured.out
    assert "user_id" in captured.out


@pytest.mark.django_db
def test_dump_session_should_report_missing_context_when_response_has_no_request(capsys):
    response = FluentResponse(HttpResponse("test"))
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "no request context" in captured.out


@pytest.mark.django_db
def test_dump_session_should_report_empty_when_session_has_no_entries(capsys):
    client = FluentHttpAssertClient(Client())
    response = client.get("/json/")
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "(empty)" in captured.out


@pytest.mark.django_db
def test_dump_cookies_should_print_cookies_when_present(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.dump_cookies()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Cookies]" in captured.out
    assert "session_id" in captured.out


@pytest.mark.django_db
def test_dump_cookies_should_return_self_when_response_has_no_cookies(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump_cookies()
    assert result is response


@pytest.mark.django_db
def test_dump_cookies_should_include_cookie_attributes_when_set(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/cookie-detailed/")
    result = response.dump_cookies()
    assert result is response
    captured = capsys.readouterr()
    assert "max-age:" in captured.out


@pytest.mark.django_db
def test_dd_should_raise_runtime_error_after_dumping_response(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(RuntimeError, match="dd\\(\\) called"):
        response.dd()
