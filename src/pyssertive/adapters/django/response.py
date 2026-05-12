from __future__ import annotations

from django.http import HttpResponse

from pyssertive.adapters.django.assertions import (
    FormValidationAssertionsMixin,
    SessionAssertionsMixin,
    TemplateContextAssertionsMixin,
)
from pyssertive.adapters.django.debug import DjangoDebugMixin
from pyssertive.adapters.django.streaming import StreamingAssertionsMixin
from pyssertive.http.response import FluentResponse as _BaseFluentResponse


class FluentResponse(
    DjangoDebugMixin,
    SessionAssertionsMixin,
    StreamingAssertionsMixin,
    TemplateContextAssertionsMixin,
    FormValidationAssertionsMixin,
    _BaseFluentResponse,
):
    """Fluent assertion wrapper for Django HTTP responses.

    Adds Django-specific assertion families (templates, forms, sessions,
    streaming responses) on top of the framework-agnostic core.

    Example::

        response = client.get("/api/users/")
        FluentResponse(response).assert_ok().assert_json_path("count", 10)
    """

    def __init__(self, response: HttpResponse) -> None:
        self._response: HttpResponse = response

    @property
    def reason_phrase(self) -> str:
        return self._response.reason_phrase
