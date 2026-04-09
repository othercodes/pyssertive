from __future__ import annotations

import re
import sys

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self
from urllib.parse import urlparse

from django.http import HttpResponse


class HttpStatusAssertionsMixin:
    _response: HttpResponse

    def assert_ok(self) -> Self:
        assert 200 <= self._response.status_code < 300, f"Expected 2xx, got {self._response.status_code}"
        return self

    def assert_created(self) -> Self:
        assert self._response.status_code == 201, f"Expected 201 Created, got {self._response.status_code}"
        return self

    def assert_accepted(self) -> Self:
        assert self._response.status_code == 202, f"Expected 202 Accepted, got {self._response.status_code}"
        return self

    def assert_no_content(self) -> Self:
        assert self._response.status_code == 204, f"Expected 204 No Content, got {self._response.status_code}"
        return self

    def assert_redirect(self, to: str | None = None) -> Self:
        assert 300 <= self._response.status_code < 400, f"Expected redirect (3xx), got {self._response.status_code}"
        if to is not None:
            location = self._response.headers.get("Location") or self._response.get("Location")
            assert location, "Redirect location header is missing"
            expected_path = urlparse(to).path
            actual_path = urlparse(location).path
            assert actual_path.endswith(expected_path), f"Expected redirect to '{to}', got '{location}'"
        return self

    def assert_moved_permanently(self) -> Self:
        assert self._response.status_code == 301, f"Expected 301 Moved Permanently, got {self._response.status_code}"
        return self

    def assert_found(self) -> Self:
        assert self._response.status_code == 302, f"Expected 302 Found (redirect), got {self._response.status_code}"
        return self

    def assert_see_other(self) -> Self:
        assert self._response.status_code == 303, f"Expected 303 See Other, got {self._response.status_code}"
        return self

    def assert_bad_request(self) -> Self:
        assert self._response.status_code == 400, f"Expected 400 Bad Request, got {self._response.status_code}"
        return self

    def assert_unauthorized(self) -> Self:
        assert self._response.status_code == 401, f"Expected 401 Unauthorized, got {self._response.status_code}"
        return self

    def assert_payment_required(self) -> Self:
        assert self._response.status_code == 402, f"Expected 402 Payment Required, got {self._response.status_code}"
        return self

    def assert_forbidden(self) -> Self:
        assert self._response.status_code == 403, f"Expected 403 Forbidden, got {self._response.status_code}"
        return self

    def assert_not_found(self) -> Self:
        assert self._response.status_code == 404, f"Expected 404 Not Found, got {self._response.status_code}"
        return self

    def assert_method_not_allowed(self) -> Self:
        assert self._response.status_code == 405, f"Expected 405 Method Not Allowed, got {self._response.status_code}"
        return self

    def assert_request_timeout(self) -> Self:
        assert self._response.status_code == 408, f"Expected 408 Request Timeout, got {self._response.status_code}"
        return self

    def assert_conflict(self) -> Self:
        assert self._response.status_code == 409, f"Expected 409 Conflict, got {self._response.status_code}"
        return self

    def assert_gone(self) -> Self:
        assert self._response.status_code == 410, f"Expected 410 Gone, got {self._response.status_code}"
        return self

    def assert_unprocessable(self) -> Self:
        assert self._response.status_code == 422, f"Expected 422 Unprocessable Entity, got {self._response.status_code}"
        return self

    def assert_too_many_requests(self) -> Self:
        assert self._response.status_code == 429, f"Expected 429 Too Many Requests, got {self._response.status_code}"
        return self

    def assert_internal_server_error(self) -> Self:
        assert self._response.status_code == 500, (
            f"Expected 500 Internal Server Error, got {self._response.status_code}"
        )
        return self

    def assert_service_unavailable(self) -> Self:
        assert self._response.status_code == 503, f"Expected 503 Service Unavailable, got {self._response.status_code}"
        return self

    def assert_server_error(self) -> Self:
        assert 500 <= self._response.status_code < 600, f"Expected 5xx Server Error, got {self._response.status_code}"
        return self

    def assert_client_error(self) -> Self:
        assert 400 <= self._response.status_code < 500, f"Expected 4xx Client Error, got {self._response.status_code}"
        return self

    def assert_status(self, status_code: int) -> Self:
        assert self._response.status_code == status_code, (
            f"Expected status {status_code}, got {self._response.status_code}"
        )
        return self


class HeaderAssertionsMixin:
    _response: HttpResponse

    def assert_header(self, name: str, value: str) -> Self:
        actual = self._response.headers.get(name)
        assert actual == value, f"Expected header '{name}' to be '{value}', got '{actual}'"
        return self

    def assert_header_contains(self, name: str, fragment: str) -> Self:
        actual = self._response.headers.get(name)
        assert actual is not None, f"Expected header '{name}' to exist"
        assert fragment in actual, f"Expected header '{name}' to contain '{fragment}', got '{actual}'"
        return self

    def assert_header_missing(self, name: str) -> Self:
        assert name not in self._response.headers, (
            f"Expected header '{name}' to be missing, but found: '{self._response.headers.get(name)}'"
        )
        return self

    def assert_content_type(self, expected: str) -> Self:
        actual = self._response.headers.get("Content-Type")
        assert actual == expected, f"Expected Content-Type '{expected}', got '{actual}'"
        return self


class CookieAssertionsMixin:
    _response: HttpResponse

    def assert_cookie(self, name: str, value: str | None = None) -> Self:
        cookies = self._response.cookies
        assert name in cookies, f"Cookie '{name}' not found. Available cookies: {list(cookies.keys())}"
        if value is not None:
            actual = cookies[name].value
            assert actual == value, f"Cookie '{name}' expected '{value}', got '{actual}'"
        return self

    def assert_cookie_missing(self, name: str) -> Self:
        cookies = self._response.cookies
        assert name not in cookies, f"Cookie '{name}' should not exist but has value '{cookies[name].value}'"
        return self

    def assert_cookie_expired(self, name: str) -> Self:
        cookies = self._response.cookies
        assert name in cookies, f"Cookie '{name}' not found"
        cookie = cookies[name]
        max_age = cookie.get("max-age")
        is_expired = max_age == 0 or max_age == "0" or cookie.value == ""
        assert is_expired, f"Cookie '{name}' is not expired (max-age={max_age}, value='{cookie.value}')"
        return self


class StreamingAssertionsMixin:
    _response: HttpResponse
    _cached_streaming_content: str

    def _get_streaming_content(self) -> str:
        # Streaming content can only be consumed once, so cache it for reuse
        from django.http import StreamingHttpResponse

        if hasattr(self, "_cached_streaming_content"):
            return self._cached_streaming_content

        if isinstance(self._response, StreamingHttpResponse):
            content = b"".join(self._response.streaming_content).decode("utf-8")
        else:
            content = self._response.content.decode("utf-8")

        self._cached_streaming_content = content
        return content

    def _get_streaming_lines(self, strip_empty: bool = True) -> list[str]:
        # Handles both \n and \r\n line endings
        content = self._get_streaming_content()
        content = content.replace("\r\n", "\n")
        lines = content.split("\n")
        if strip_empty:
            lines = [line for line in lines if line.strip()]
        return lines

    def assert_streaming(self) -> Self:
        from django.http import StreamingHttpResponse

        assert isinstance(self._response, StreamingHttpResponse), (
            f"Expected StreamingHttpResponse, got {type(self._response).__name__}"
        )
        return self

    def assert_download(self, filename: str | None = None) -> Self:
        # If filename provided, also asserts the filename matches.
        disposition = self._response.get("Content-Disposition", "")
        assert "attachment" in disposition, f"Expected Content-Disposition: attachment header, got '{disposition}'"
        if filename is not None:
            assert f'filename="{filename}"' in disposition or f"filename={filename}" in disposition, (
                f"Expected filename '{filename}' in Content-Disposition, got '{disposition}'"
            )
        return self

    def assert_streaming_contains(self, text: str) -> Self:
        content = self._get_streaming_content()
        assert text in content, f"Expected streaming content to contain '{text}'"
        return self

    def assert_streaming_not_contains(self, text: str) -> Self:
        content = self._get_streaming_content()
        assert text not in content, f"Expected streaming content to NOT contain '{text}'"
        return self

    def assert_streaming_matches(self, pattern: str) -> Self:
        content = self._get_streaming_content()
        assert re.search(pattern, content), f"Expected streaming content to match pattern '{pattern}'"
        return self

    def assert_streaming_line_count(
        self, exact: int | None = None, *, min: int | None = None, max: int | None = None
    ) -> Self:
        # Counts non-empty lines only
        lines = self._get_streaming_lines()
        count = len(lines)

        if exact is not None:
            assert count == exact, f"Expected exactly {exact} lines, got {count}"
        if min is not None:
            assert count >= min, f"Expected at least {min} lines, got {count}"
        if max is not None:
            assert count <= max, f"Expected at most {max} lines, got {count}"

        return self

    def assert_streaming_empty(self) -> Self:
        # Checks for no non-empty lines
        lines = self._get_streaming_lines()
        assert len(lines) == 0, f"Expected empty streaming content, got {len(lines)} lines"
        return self

    def assert_streaming_csv_header(self, columns: list[str] | str) -> Self:
        # columns: list of names or comma-separated string
        lines = self._get_streaming_lines(strip_empty=False)
        has_content = len(lines) > 0 and lines[0].strip()
        assert has_content, "Expected CSV content but response is empty"

        header = lines[0]
        expected = ",".join(columns) if isinstance(columns, list) else columns

        assert header == expected, f"Expected CSV header '{expected}', got '{header}'"
        return self

    def assert_streaming_line(self, index: int, expected: str) -> Self:
        lines = self._get_streaming_lines()
        assert index < len(lines), f"Line index {index} out of range (only {len(lines)} lines)"
        actual = lines[index]
        assert actual == expected, f"Line {index}: expected '{expected}', got '{actual}'"
        return self
