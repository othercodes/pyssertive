from __future__ import annotations

import pytest

from tests.adapters._factories import RESPONSE_FACTORIES


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_fluent_response_should_expose_wrapped_native(make_response):
    response = make_response()
    assert response.wrapped is not None


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_fluent_response_should_return_self_for_method_chaining(make_response):
    response = make_response()
    assert response.assert_ok() is response


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_fluent_response_should_raise_attribute_error_for_truly_unknown_attribute(make_response):
    response = make_response()
    with pytest.raises(AttributeError):
        _ = response.this_does_not_exist


@pytest.mark.parametrize("make_response", RESPONSE_FACTORIES)
def test_fluent_response_should_expose_charset_property(make_response):
    response = make_response()
    assert response.charset is None or isinstance(response.charset, str)
