from __future__ import annotations

import pytest

from pyssertive.http.response import ResponseProtocol
from tests.adapters._factories import RESPONSE_FACTORIES


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_fluent_response_should_satisfy_http_response_protocol(make_response):
    response = make_response()
    assert isinstance(response, ResponseProtocol)
