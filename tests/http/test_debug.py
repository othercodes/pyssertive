import pytest
from django.http import HttpResponse
from django.test import Client

from pyssertive.http.client import FluentHttpAssertClient, FluentResponse


@pytest.mark.django_db
def test_dump_json(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Dump" in captured.out
    assert "200" in captured.out


@pytest.mark.django_db
def test_dump_plain_text(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/plain-text/")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "Plain text content" in captured.out


@pytest.mark.django_db
def test_dump_with_explicit_format(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump(content_format="text/plain")
    assert result is response
    captured = capsys.readouterr()
    assert "text/plain" in captured.out


@pytest.mark.django_db
def test_dump_invalid_json(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/invalid-json/")
    result = response.dump(content_format="application/json")
    assert result is response
    captured = capsys.readouterr()
    assert "[Invalid JSON]" in captured.out


@pytest.mark.django_db
def test_dump_html(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/html/")
    result = response.dump()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Dump" in captured.out


@pytest.mark.django_db
def test_dump_headers(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/custom-headers/")
    result = response.dump_headers()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Headers]" in captured.out
    assert "X-Custom-Header" in captured.out


@pytest.mark.django_db
def test_dump_json_method(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump_json()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response JSON]" in captured.out
    assert '"ok": true' in captured.out


@pytest.mark.django_db
def test_dump_json_fails_for_invalid(fluent_admin_client):
    response = fluent_admin_client.get("/invalid-json/")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.dump_json()


@pytest.mark.django_db
def test_dump_session(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/session-set/")
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "[Session Data]" in captured.out
    assert "user_id" in captured.out


@pytest.mark.django_db
def test_dump_session_without_context(capsys):
    response = FluentResponse(HttpResponse("test"))
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "no request context" in captured.out


@pytest.mark.django_db
def test_dump_session_empty(capsys):
    client = FluentHttpAssertClient(Client())
    response = client.get("/json/")
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "(empty)" in captured.out


@pytest.mark.django_db
def test_dump_cookies(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/cookie-set/")
    result = response.dump_cookies()
    assert result is response
    captured = capsys.readouterr()
    assert "[Response Cookies]" in captured.out
    assert "session_id" in captured.out


@pytest.mark.django_db
def test_dump_cookies_empty(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/json/")
    result = response.dump_cookies()
    assert result is response


@pytest.mark.django_db
def test_dump_cookies_with_details(fluent_admin_client, capsys):
    response = fluent_admin_client.get("/cookie-detailed/")
    result = response.dump_cookies()
    assert result is response
    captured = capsys.readouterr()
    assert "max-age:" in captured.out


@pytest.mark.django_db
def test_dd(fluent_admin_client):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(RuntimeError, match="dd\\(\\) called"):
        response.dd()
