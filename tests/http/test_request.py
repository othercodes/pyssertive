import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory

from pyssertive.http.request import RequestBuilder


@pytest.fixture
def rf():
    return RequestFactory()


def test_request_builder_default_get(rf):
    request = RequestBuilder(rf).build()
    assert request.method == "GET"
    assert request.path == "/"


def test_request_builder_without_factory():
    request = RequestBuilder().build()
    assert request.method == "GET"
    assert request.path == "/"


def test_request_builder_with_method(rf):
    request = RequestBuilder(rf).with_method("POST").build()
    assert request.method == "POST"


def test_request_builder_with_path(rf):
    request = RequestBuilder(rf).with_path("/api/users/").build()
    assert request.path == "/api/users/"


def test_request_builder_with_data_get(rf):
    request = RequestBuilder(rf).with_data({"page": "1"}).build()
    assert request.GET.get("page") == "1"


def test_request_builder_with_data_post(rf):
    request = RequestBuilder(rf).with_method("POST").with_data({"name": "John"}).build()
    assert request.POST.get("name") == "John"


@pytest.mark.django_db
def test_request_builder_with_user(rf):
    user = User.objects.create_user(username="testuser", password="testpass")
    request = RequestBuilder(rf).with_user(user).build()
    assert request.user == user


def test_request_builder_with_cookie(rf):
    request = RequestBuilder(rf).with_cookie("session", "abc123").build()
    assert request.COOKIES.get("session") == "abc123"


def test_request_builder_with_cookies(rf):
    request = RequestBuilder(rf).with_cookies({"session": "abc", "token": "xyz"}).build()
    assert request.COOKIES.get("session") == "abc"
    assert request.COOKIES.get("token") == "xyz"


def test_request_builder_with_meta(rf):
    request = RequestBuilder(rf).with_meta("HTTP_X_FORWARDED_FOR", "192.168.1.1").build()
    assert request.META.get("HTTP_X_FORWARDED_FOR") == "192.168.1.1"


def test_request_builder_with_header(rf):
    request = RequestBuilder(rf).with_header("X-Custom-Header", "custom-value").build()
    assert request.headers.get("X-Custom-Header") == "custom-value"


def test_request_builder_with_headers(rf):
    request = RequestBuilder(rf).with_headers({"X-One": "1", "X-Two": "2"}).build()
    assert request.headers.get("X-One") == "1"
    assert request.headers.get("X-Two") == "2"


def test_request_builder_with_property(rf):
    request = RequestBuilder(rf).with_property("custom_attr", "custom_value").build()
    assert request.custom_attr == "custom_value"


def test_request_builder_put_method(rf):
    request = RequestBuilder(rf).with_method("PUT").with_data({"id": "1"}).build()
    assert request.method == "PUT"


def test_request_builder_patch_method(rf):
    request = RequestBuilder(rf).with_method("PATCH").with_data({"name": "Updated"}).build()
    assert request.method == "PATCH"


def test_request_builder_delete_method(rf):
    request = RequestBuilder(rf).with_method("DELETE").build()
    assert request.method == "DELETE"


def test_request_builder_head_method(rf):
    request = RequestBuilder(rf).with_method("HEAD").build()
    assert request.method == "HEAD"


def test_request_builder_options_method(rf):
    request = RequestBuilder(rf).with_method("OPTIONS").build()
    assert request.method == "OPTIONS"


def test_request_builder_unsupported_method(rf):
    with pytest.raises(ValueError, match="Unsupported HTTP method"):
        RequestBuilder(rf).with_method("INVALID").build()


def test_request_builder_chaining(rf):
    request = (
        RequestBuilder(rf)
        .with_method("POST")
        .with_path("/api/create/")
        .with_data({"name": "Test"})
        .with_cookie("auth", "token123")
        .with_meta("REMOTE_ADDR", "127.0.0.1")
        .with_header("Accept", "application/json")
        .with_property("tracking_id", "xyz")
        .build()
    )
    assert request.method == "POST"
    assert request.path == "/api/create/"
    assert request.POST.get("name") == "Test"
    assert request.COOKIES.get("auth") == "token123"
    assert request.META.get("REMOTE_ADDR") == "127.0.0.1"
    assert request.headers.get("Accept") == "application/json"
    assert request.tracking_id == "xyz"


def test_request_builder_init_with_params(rf):
    request = RequestBuilder(rf, method="POST", path="/custom/", data={"key": "value"}).build()
    assert request.method == "POST"
    assert request.path == "/custom/"
    assert request.POST.get("key") == "value"


def test_request_builder_with_body_post(rf):
    request = RequestBuilder(rf).with_method("POST").with_body({"name": "John"}).build()
    assert request.POST.get("name") == "John"


def test_request_builder_with_body_put(rf):
    request = RequestBuilder(rf).with_method("PUT").with_body({"name": "John"}).build()
    assert request.method == "PUT"


def test_request_builder_with_body_patch(rf):
    request = RequestBuilder(rf).with_method("PATCH").with_body({"name": "John"}).build()
    assert request.method == "PATCH"


def test_request_builder_with_body_fails_for_get(rf):
    with pytest.raises(ValueError, match="Cannot set body on GET request"):
        RequestBuilder(rf).with_method("GET").with_body({"name": "John"})


def test_request_builder_with_body_fails_for_delete(rf):
    with pytest.raises(ValueError, match="Cannot set body on DELETE request"):
        RequestBuilder(rf).with_method("DELETE").with_body({"name": "John"})


def test_request_builder_with_query_string_get(rf):
    request = RequestBuilder(rf).with_method("GET").with_query_string({"page": "1"}).build()
    assert request.GET.get("page") == "1"


def test_request_builder_with_query_string_post(rf):
    request = RequestBuilder(rf).with_method("POST").with_query_string({"source": "api"}).build()
    assert request.method == "POST"


def test_request_builder_with_query_string_delete(rf):
    request = RequestBuilder(rf).with_method("DELETE").with_query_string({"id": "123"}).build()
    assert request.method == "DELETE"
