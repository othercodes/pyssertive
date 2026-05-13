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
    def __init__(self, response: HttpResponse) -> None:
        self._response: HttpResponse = response

    @property
    def reason_phrase(self) -> str:
        return self._response.reason_phrase
