from __future__ import annotations

import re
import sys

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from django.http import HttpResponse


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
