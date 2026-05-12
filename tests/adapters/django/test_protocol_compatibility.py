from __future__ import annotations

from django.http import HttpResponse

from pyssertive.protocol import HttpResponseProtocol


def test_django_http_response_should_satisfy_http_response_protocol() -> None:
    response = HttpResponse(b"body", status=200, charset="utf-8")

    assert isinstance(response, HttpResponseProtocol)
