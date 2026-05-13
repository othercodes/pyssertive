import pytest
from django.http import HttpResponse
from django.test import Client

from pyssertive.adapters.django import FluentHttpAssertClient, FluentResponse


@pytest.mark.django_db
def test_dump_session_should_print_session_entries_when_session_populated(
    fluent_admin_client: FluentHttpAssertClient, capsys: pytest.CaptureFixture[str]
):
    response = fluent_admin_client.get("/session-set/")
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "[Session Data]" in captured.out
    assert "user_id" in captured.out


@pytest.mark.django_db
def test_dump_session_should_report_missing_context_when_response_has_no_request(capsys: pytest.CaptureFixture[str]):
    response = FluentResponse(HttpResponse("test"))
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "no request context" in captured.out


@pytest.mark.django_db
def test_dump_session_should_report_empty_when_session_has_no_entries(capsys: pytest.CaptureFixture[str]):
    client = FluentHttpAssertClient(Client())
    response = client.get("/json/")
    result = response.dump_session()
    assert result is response
    captured = capsys.readouterr()
    assert "(empty)" in captured.out
