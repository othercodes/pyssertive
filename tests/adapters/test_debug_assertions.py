from __future__ import annotations

import pytest

from tests.adapters._factories import RESPONSE_FACTORIES

SIMPLE = {"ok": True}


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_should_pretty_print_json_when_content_type_is_json(make_response, capsys):
    response = make_response(body=SIMPLE, content_type="application/json")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Dump" in captured.out
    assert "200" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_should_print_body_when_content_type_is_plain_text(make_response, capsys):
    response = make_response(body="Plain text content", content_type="text/plain")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "Plain text content" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_should_use_explicit_content_format_when_provided(make_response, capsys):
    response = make_response(body=SIMPLE, content_type="application/json")
    result = response.dump(content_format="text/plain")
    assert result is response
    captured = capsys.readouterr()
    assert "text/plain" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_should_report_invalid_json_when_payload_cannot_be_parsed(make_response, capsys):
    response = make_response(body="not valid json", content_type="application/json")
    result = response.dump(content_format="application/json")
    assert result is response
    captured = capsys.readouterr()
    assert "[Invalid JSON]" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_should_print_raw_body_when_content_type_is_unknown(make_response, capsys):
    response = make_response(body="<html></html>", content_type="text/html")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Dump" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_headers_should_print_all_response_headers(make_response, capsys):
    response = make_response(headers={"X-Custom-Header": "custom-value"})
    result = response.dump_headers()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Headers]" in captured.out
    assert "x-custom-header" in captured.out.lower()


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_json_should_pretty_print_payload_when_valid(make_response, capsys):
    response = make_response(body=SIMPLE, content_type="application/json")
    result = response.dump_json()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response JSON]" in captured.out
    assert '"ok": true' in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_json_should_raise_when_payload_is_invalid(make_response):
    response = make_response(body="not valid json", content_type="application/json")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.dump_json()


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_cookies_should_print_cookies_when_present(make_response, capsys):
    response = make_response(cookies={"session_id": {"value": "abc123"}})
    result = response.dump_cookies()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Cookies]" in captured.out
    assert "session_id" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_cookies_should_return_self_when_response_has_no_cookies(make_response):
    response = make_response()
    assert response.dump_cookies() is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dump_cookies_should_include_cookie_attributes_when_set(make_response, capsys):
    response = make_response(cookies={"detailed": {"value": "data", "max_age": 3600}})
    result = response.dump_cookies()
    assert result is response
    captured = capsys.readouterr()
    assert "max-age:" in captured.out


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_dd_should_raise_runtime_error_after_dumping_response(make_response):
    response = make_response()
    with pytest.raises(RuntimeError, match="dd\\(\\) called"):
        response.dd()
