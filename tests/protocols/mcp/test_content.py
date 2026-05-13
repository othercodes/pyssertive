from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _call_with(content: list) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "result": {"content": content}}


def test_is_text_should_pass_for_text_block():
    AssertableMCP(_call_with([{"type": "text", "text": "hi"}])).tool("x").content(0, lambda c: c.is_text())


def test_is_text_should_raise_for_non_text_block():
    payload = _call_with([{"type": "image", "mimeType": "image/png", "data": "Zm9v"}])
    with pytest.raises(AssertionError, match="expected 'text'"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.is_text())


def test_is_image_should_pass_for_image_block():
    payload = _call_with([{"type": "image", "mimeType": "image/png", "data": "Zm9v"}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.is_image())


def test_is_audio_should_pass_for_audio_block():
    payload = _call_with([{"type": "audio", "mimeType": "audio/mpeg", "data": "Zm9v"}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.is_audio())


def test_is_resource_link_should_pass():
    payload = _call_with([{"type": "resource_link", "uri": "file:///main.py", "name": "main.py"}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.is_resource_link())


def test_is_resource_should_pass():
    payload = _call_with([{"type": "resource", "resource": {"uri": "file:///x", "text": "hi"}}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.is_resource())


def test_text_equals_should_pass_when_text_matches():
    AssertableMCP(_call_with([{"type": "text", "text": "abc"}])).tool("x").content(0, lambda c: c.text_equals("abc"))


def test_text_equals_should_raise_when_text_differs():
    payload = _call_with([{"type": "text", "text": "abc"}])
    with pytest.raises(AssertionError, match="expected 'xyz'"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.text_equals("xyz"))


def test_text_contains_should_pass_when_substring_present():
    payload = _call_with([{"type": "text", "text": "hello world"}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.text_contains("world"))


def test_text_contains_should_raise_when_substring_absent():
    payload = _call_with([{"type": "text", "text": "hello"}])
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.text_contains("world"))


def test_with_mime_type_should_pass_when_mime_matches():
    payload = _call_with([{"type": "image", "mimeType": "image/png", "data": "Zm9v"}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.is_image().with_mime_type("image/png"))


def test_with_mime_type_should_raise_when_mime_differs():
    payload = _call_with([{"type": "image", "mimeType": "image/jpeg", "data": "Zm9v"}])
    with pytest.raises(AssertionError, match="mimeType"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_mime_type("image/png"))


def test_with_base64_data_should_pass_for_valid_base64_payload():
    payload = _call_with([{"type": "image", "mimeType": "image/png", "data": "aGVsbG8="}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.is_image().with_base64_data())


def test_with_base64_data_should_raise_when_data_missing():
    payload = _call_with([{"type": "image", "mimeType": "image/png", "data": ""}])
    with pytest.raises(AssertionError, match="missing or empty"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_base64_data())


def test_with_base64_data_should_raise_when_data_invalid():
    payload = _call_with([{"type": "image", "mimeType": "image/png", "data": "%%%not-base64"}])
    with pytest.raises(AssertionError, match="not valid base64"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_base64_data())


def test_with_uri_should_pass_for_resource_link_block():
    payload = _call_with([{"type": "resource_link", "uri": "file:///main.py"}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.with_uri("file:///main.py"))


def test_with_uri_should_pass_for_resource_block_nested_uri():
    payload = _call_with([{"type": "resource", "resource": {"uri": "file:///x.py", "text": "y"}}])
    AssertableMCP(payload).tool("x").content(0, lambda c: c.with_uri("file:///x.py"))


def test_with_uri_should_raise_when_uri_differs():
    payload = _call_with([{"type": "resource_link", "uri": "file:///wrong.py"}])
    with pytest.raises(AssertionError, match="uri"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_uri("file:///main.py"))


def test_require_type_should_raise_when_block_is_not_dict():
    payload = _call_with(["not-a-block"])
    with pytest.raises(AssertionError, match="not a dict"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.is_text())


def test_with_mime_type_should_raise_when_block_is_not_dict():
    payload = _call_with(["not-a-block"])
    with pytest.raises(AssertionError, match="not a dict"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_mime_type("image/png"))


def test_with_base64_data_should_raise_when_block_is_not_dict():
    payload = _call_with(["not-a-block"])
    with pytest.raises(AssertionError, match="not a dict"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_base64_data())


def test_with_uri_should_raise_when_block_is_not_dict():
    payload = _call_with(["not-a-block"])
    with pytest.raises(AssertionError, match="not a dict"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.with_uri("file:///x"))


def test_text_equals_kind_should_mention_unknown_type_when_type_absent():
    payload = _call_with([{}])
    with pytest.raises(AssertionError, match="'<unknown>'"):
        AssertableMCP(payload).tool("x").content(0, lambda c: c.is_text())
