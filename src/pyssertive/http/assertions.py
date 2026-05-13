from __future__ import annotations

import sys
from typing import Any
from urllib.parse import urlparse

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


class HttpStatusAssertionsMixin:
    status_code: int
    headers: Any

    def assert_ok(self) -> Self:
        assert 200 <= self.status_code < 300, f"Expected 2xx, got {self.status_code}"
        return self

    def assert_created(self) -> Self:
        assert self.status_code == 201, f"Expected 201 Created, got {self.status_code}"
        return self

    def assert_accepted(self) -> Self:
        assert self.status_code == 202, f"Expected 202 Accepted, got {self.status_code}"
        return self

    def assert_no_content(self) -> Self:
        assert self.status_code == 204, f"Expected 204 No Content, got {self.status_code}"
        return self

    def assert_redirect(self, to: str | None = None) -> Self:
        assert 300 <= self.status_code < 400, f"Expected redirect (3xx), got {self.status_code}"
        if to is not None:
            location = self.headers.get("Location")
            assert location, "Redirect location header is missing"
            expected_path = urlparse(to).path
            actual_path = urlparse(location).path
            assert actual_path.endswith(expected_path), f"Expected redirect to '{to}', got '{location}'"
        return self

    def assert_moved_permanently(self) -> Self:
        assert self.status_code == 301, f"Expected 301 Moved Permanently, got {self.status_code}"
        return self

    def assert_found(self) -> Self:
        assert self.status_code == 302, f"Expected 302 Found (redirect), got {self.status_code}"
        return self

    def assert_see_other(self) -> Self:
        assert self.status_code == 303, f"Expected 303 See Other, got {self.status_code}"
        return self

    def assert_bad_request(self) -> Self:
        assert self.status_code == 400, f"Expected 400 Bad Request, got {self.status_code}"
        return self

    def assert_unauthorized(self) -> Self:
        assert self.status_code == 401, f"Expected 401 Unauthorized, got {self.status_code}"
        return self

    def assert_payment_required(self) -> Self:
        assert self.status_code == 402, f"Expected 402 Payment Required, got {self.status_code}"
        return self

    def assert_forbidden(self) -> Self:
        assert self.status_code == 403, f"Expected 403 Forbidden, got {self.status_code}"
        return self

    def assert_not_found(self) -> Self:
        assert self.status_code == 404, f"Expected 404 Not Found, got {self.status_code}"
        return self

    def assert_method_not_allowed(self) -> Self:
        assert self.status_code == 405, f"Expected 405 Method Not Allowed, got {self.status_code}"
        return self

    def assert_request_timeout(self) -> Self:
        assert self.status_code == 408, f"Expected 408 Request Timeout, got {self.status_code}"
        return self

    def assert_conflict(self) -> Self:
        assert self.status_code == 409, f"Expected 409 Conflict, got {self.status_code}"
        return self

    def assert_gone(self) -> Self:
        assert self.status_code == 410, f"Expected 410 Gone, got {self.status_code}"
        return self

    def assert_unprocessable(self) -> Self:
        assert self.status_code == 422, f"Expected 422 Unprocessable Entity, got {self.status_code}"
        return self

    def assert_too_many_requests(self) -> Self:
        assert self.status_code == 429, f"Expected 429 Too Many Requests, got {self.status_code}"
        return self

    def assert_internal_server_error(self) -> Self:
        assert self.status_code == 500, f"Expected 500 Internal Server Error, got {self.status_code}"
        return self

    def assert_service_unavailable(self) -> Self:
        assert self.status_code == 503, f"Expected 503 Service Unavailable, got {self.status_code}"
        return self

    def assert_server_error(self) -> Self:
        assert 500 <= self.status_code < 600, f"Expected 5xx Server Error, got {self.status_code}"
        return self

    def assert_client_error(self) -> Self:
        assert 400 <= self.status_code < 500, f"Expected 4xx Client Error, got {self.status_code}"
        return self

    def assert_status(self, status_code: int) -> Self:
        assert self.status_code == status_code, f"Expected status {status_code}, got {self.status_code}"
        return self


class HeaderAssertionsMixin:
    headers: Any

    def assert_header(self, name: str, value: str) -> Self:
        actual = self.headers.get(name)
        assert actual == value, f"Expected header '{name}' to be '{value}', got '{actual}'"
        return self

    def assert_header_contains(self, name: str, fragment: str) -> Self:
        actual = self.headers.get(name)
        assert actual is not None, f"Expected header '{name}' to exist"
        assert fragment in actual, f"Expected header '{name}' to contain '{fragment}', got '{actual}'"
        return self

    def assert_header_missing(self, name: str) -> Self:
        assert name not in self.headers, (
            f"Expected header '{name}' to be missing, but found: '{self.headers.get(name)}'"
        )
        return self

    def assert_content_type(self, expected: str) -> Self:
        actual = self.headers.get("Content-Type")
        assert actual == expected, f"Expected Content-Type '{expected}', got '{actual}'"
        return self


class CookieAssertionsMixin:
    cookies: Any

    def assert_cookie(self, name: str, value: str | None = None) -> Self:
        cookies = self.cookies
        assert name in cookies, f"Cookie '{name}' not found. Available cookies: {list(cookies.keys())}"
        if value is not None:
            actual = cookies[name].value
            assert actual == value, f"Cookie '{name}' expected '{value}', got '{actual}'"
        return self

    def assert_cookie_missing(self, name: str) -> Self:
        cookies = self.cookies
        assert name not in cookies, f"Cookie '{name}' should not exist but has value '{cookies[name].value}'"
        return self

    def assert_cookie_expired(self, name: str) -> Self:
        cookies = self.cookies
        assert name in cookies, f"Cookie '{name}' not found"
        cookie = cookies[name]
        max_age = cookie.get("max-age")
        is_expired = max_age == 0 or max_age == "0" or cookie.value == ""
        assert is_expired, f"Cookie '{name}' is not expired (max-age={max_age}, value='{cookie.value}')"
        return self
