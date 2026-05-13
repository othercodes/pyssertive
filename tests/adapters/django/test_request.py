import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from pyssertive.adapters.django import DjangoRequestBuilder


@pytest.fixture
def rf():
    return RequestFactory()


def test_request_builder_should_raise_when_method_is_unsupported(rf: RequestFactory):
    with pytest.raises(ValueError, match="Unsupported HTTP method"):
        DjangoRequestBuilder(rf).with_method("INVALID").build()


@pytest.mark.django_db
def test_request_builder_should_attach_authenticated_user(rf: RequestFactory):
    user = User.objects.create_user(username="testuser", password="testpass")
    request = DjangoRequestBuilder(rf).with_user(user).build()
    assert request.user == user


def test_request_builder_should_set_meta_value(rf: RequestFactory):
    request = DjangoRequestBuilder(rf).with_meta("HTTP_X_FORWARDED_FOR", "192.168.1.1").build()
    assert request.META.get("HTTP_X_FORWARDED_FOR") == "192.168.1.1"


def test_request_builder_should_attach_custom_property(rf: RequestFactory):
    request = DjangoRequestBuilder(rf).with_property("custom_attr", "custom_value").build()
    assert request.custom_attr == "custom_value"  # type: ignore[attr-defined]
