from __future__ import annotations

import pytest

from pyssertive.protocols.mcp.content import (
    AssertableAudioContent,
    AssertableContent,
    AssertableImageContent,
    AssertableResourceContent,
    AssertableResourceLinkContent,
    AssertableTextContent,
)


@pytest.mark.parametrize(
    ("guard", "block", "typed_class"),
    [
        ("is_text", {"type": "text", "text": "hi"}, AssertableTextContent),
        ("is_image", {"type": "image", "mimeType": "image/png", "data": "Zm9v"}, AssertableImageContent),
        ("is_audio", {"type": "audio", "mimeType": "audio/mpeg", "data": "Zm9v"}, AssertableAudioContent),
        ("is_resource_link", {"type": "resource_link", "uri": "file:///x"}, AssertableResourceLinkContent),
        ("is_resource", {"type": "resource", "resource": {"uri": "file:///x"}}, AssertableResourceContent),
    ],
)
def test_type_guard_should_return_typed_subclass_when_no_callback(guard, block, typed_class):
    content = AssertableContent(block, label="Content[0]")
    typed = getattr(content, guard)()
    assert isinstance(typed, typed_class)


@pytest.mark.parametrize(
    ("guard", "wrong_block"),
    [
        ("is_text", {"type": "image"}),
        ("is_image", {"type": "text"}),
        ("is_audio", {"type": "text"}),
        ("is_resource_link", {"type": "resource"}),
        ("is_resource", {"type": "resource_link"}),
    ],
)
def test_type_guard_should_raise_when_block_is_wrong_type(guard, wrong_block):
    content = AssertableContent(wrong_block, label="Content[0]")
    with pytest.raises(AssertionError, match="expected"):
        getattr(content, guard)()


@pytest.mark.parametrize(
    ("guard", "block", "typed_class"),
    [
        ("is_text", {"type": "text", "text": "hi"}, AssertableTextContent),
        ("is_image", {"type": "image", "mimeType": "image/png", "data": "Zm9v"}, AssertableImageContent),
        ("is_audio", {"type": "audio", "mimeType": "audio/mpeg", "data": "Zm9v"}, AssertableAudioContent),
        ("is_resource_link", {"type": "resource_link", "uri": "file:///x"}, AssertableResourceLinkContent),
        ("is_resource", {"type": "resource", "resource": {"uri": "file:///x"}}, AssertableResourceContent),
    ],
)
def test_type_guard_should_invoke_callback_with_typed_subclass_and_return_self(guard, block, typed_class):
    content = AssertableContent(block, label="Content[0]")
    received: list = []
    result = getattr(content, guard)(lambda t: received.append(t))
    assert len(received) == 1
    assert isinstance(received[0], typed_class)
    assert result is content


def test_type_guard_should_raise_before_invoking_callback_when_block_is_wrong_type():
    content = AssertableContent({"type": "image"}, label="Content[0]")
    called: list = []
    with pytest.raises(AssertionError, match="expected"):
        content.is_text(lambda t: called.append(t))
    assert called == []


def test_type_guard_should_raise_when_block_is_not_a_dict():
    content = AssertableContent("not-a-dict", label="Content[0]")
    with pytest.raises(AssertionError, match="not a dict"):
        content.is_text()


def test_type_guard_should_mention_unknown_type_when_type_field_absent():
    content = AssertableContent({}, label="Content[0]")
    with pytest.raises(AssertionError, match="'<unknown>'"):
        content.is_text()


@pytest.mark.parametrize(
    "typed_class",
    [
        AssertableTextContent,
        AssertableImageContent,
        AssertableAudioContent,
        AssertableResourceLinkContent,
        AssertableResourceContent,
    ],
)
def test_typed_content_should_raise_when_constructed_with_non_dict_block(typed_class):
    with pytest.raises(AssertionError, match="not a dict"):
        typed_class("not-a-dict", label="Content[0]")


@pytest.mark.parametrize(
    ("typed_class", "wrong_block"),
    [
        (AssertableTextContent, {"type": "image"}),
        (AssertableImageContent, {"type": "text"}),
        (AssertableAudioContent, {"type": "text"}),
        (AssertableResourceLinkContent, {"type": "resource"}),
        (AssertableResourceContent, {"type": "resource_link"}),
    ],
)
def test_typed_content_should_raise_when_constructed_with_wrong_type(typed_class, wrong_block):
    with pytest.raises(AssertionError, match="expected"):
        typed_class(wrong_block, label="Content[0]")


def test_resource_content_should_raise_when_resource_field_absent():
    with pytest.raises(AssertionError, match="resource is not a dict"):
        AssertableResourceContent({"type": "resource"}, label="Content[0]")


def test_resource_content_should_raise_when_resource_field_is_not_a_dict():
    with pytest.raises(AssertionError, match="resource is not a dict"):
        AssertableResourceContent({"type": "resource", "resource": "not-a-dict"}, label="Content[0]")


def test_text_with_text_should_pass_when_text_matches():
    typed = AssertableTextContent({"type": "text", "text": "abc"}, label="Content[0]")
    typed.with_text("abc")


def test_text_with_text_should_raise_when_text_differs():
    typed = AssertableTextContent({"type": "text", "text": "abc"}, label="Content[0]")
    with pytest.raises(AssertionError, match="expected 'xyz'"):
        typed.with_text("xyz")


def test_text_with_text_containing_should_pass_when_substring_present():
    typed = AssertableTextContent({"type": "text", "text": "hello world"}, label="Content[0]")
    typed.with_text_containing("world")


def test_text_with_text_containing_should_raise_when_substring_absent():
    typed = AssertableTextContent({"type": "text", "text": "hello"}, label="Content[0]")
    with pytest.raises(AssertionError, match="does not contain"):
        typed.with_text_containing("world")


def test_text_is_not_empty_should_pass_when_text_truthy():
    typed = AssertableTextContent({"type": "text", "text": "hi"}, label="Content[0]")
    typed.is_not_empty()


def test_text_is_not_empty_should_raise_when_text_empty():
    typed = AssertableTextContent({"type": "text", "text": ""}, label="Content[0]")
    with pytest.raises(AssertionError, match="empty"):
        typed.is_not_empty()


def test_text_is_not_empty_should_raise_when_text_field_absent():
    typed = AssertableTextContent({"type": "text"}, label="Content[0]")
    with pytest.raises(AssertionError, match="empty"):
        typed.is_not_empty()


def test_image_with_mime_type_should_pass_when_matches():
    typed = AssertableImageContent({"type": "image", "mimeType": "image/png", "data": "Zm9v"}, label="Content[0]")
    typed.with_mime_type("image/png")


def test_image_with_mime_type_should_raise_when_differs():
    typed = AssertableImageContent({"type": "image", "mimeType": "image/jpeg"}, label="Content[0]")
    with pytest.raises(AssertionError, match="mimeType"):
        typed.with_mime_type("image/png")


def test_image_with_base64_data_should_pass_for_valid_base64():
    typed = AssertableImageContent({"type": "image", "data": "aGVsbG8="}, label="Content[0]")
    typed.with_base64_data()


def test_image_with_base64_data_should_raise_when_data_missing():
    typed = AssertableImageContent({"type": "image", "data": ""}, label="Content[0]")
    with pytest.raises(AssertionError, match="missing or empty"):
        typed.with_base64_data()


def test_image_with_base64_data_should_raise_when_data_invalid():
    typed = AssertableImageContent({"type": "image", "data": "%%%not-base64"}, label="Content[0]")
    with pytest.raises(AssertionError, match="not valid base64"):
        typed.with_base64_data()


def test_audio_with_mime_type_should_pass_when_matches():
    typed = AssertableAudioContent({"type": "audio", "mimeType": "audio/mpeg", "data": "Zm9v"}, label="Content[0]")
    typed.with_mime_type("audio/mpeg")


def test_audio_with_mime_type_should_raise_when_differs():
    typed = AssertableAudioContent({"type": "audio", "mimeType": "audio/wav"}, label="Content[0]")
    with pytest.raises(AssertionError, match="mimeType"):
        typed.with_mime_type("audio/mpeg")


def test_audio_with_base64_data_should_pass_for_valid_base64():
    typed = AssertableAudioContent({"type": "audio", "data": "aGVsbG8="}, label="Content[0]")
    typed.with_base64_data()


def test_audio_with_base64_data_should_raise_when_data_invalid():
    typed = AssertableAudioContent({"type": "audio", "data": "%%%not-base64"}, label="Content[0]")
    with pytest.raises(AssertionError, match="not valid base64"):
        typed.with_base64_data()


def test_resource_link_with_uri_should_pass_when_matches():
    typed = AssertableResourceLinkContent({"type": "resource_link", "uri": "file:///main.py"}, label="Content[0]")
    typed.with_uri("file:///main.py")


def test_resource_link_with_uri_should_raise_when_differs():
    typed = AssertableResourceLinkContent({"type": "resource_link", "uri": "file:///wrong.py"}, label="Content[0]")
    with pytest.raises(AssertionError, match="uri"):
        typed.with_uri("file:///main.py")


def test_resource_link_named_should_pass_when_matches():
    typed = AssertableResourceLinkContent({"type": "resource_link", "uri": "x", "name": "main.py"}, label="Content[0]")
    typed.named("main.py")


def test_resource_link_named_should_raise_when_differs():
    typed = AssertableResourceLinkContent({"type": "resource_link", "uri": "x", "name": "other.py"}, label="Content[0]")
    with pytest.raises(AssertionError, match="name"):
        typed.named("main.py")


def test_resource_link_named_should_raise_when_name_field_absent():
    typed = AssertableResourceLinkContent({"type": "resource_link", "uri": "x"}, label="Content[0]")
    with pytest.raises(AssertionError, match="name"):
        typed.named("main.py")


def test_resource_link_with_mime_type_should_pass_when_matches():
    typed = AssertableResourceLinkContent(
        {"type": "resource_link", "uri": "x", "mimeType": "text/x-python"}, label="Content[0]"
    )
    typed.with_mime_type("text/x-python")


def test_resource_link_with_mime_type_should_raise_when_differs():
    typed = AssertableResourceLinkContent(
        {"type": "resource_link", "uri": "x", "mimeType": "text/plain"}, label="Content[0]"
    )
    with pytest.raises(AssertionError, match="mimeType"):
        typed.with_mime_type("text/x-python")


def test_resource_with_uri_should_pass_for_embedded_uri():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "file:///x.py", "text": "y"}}, label="Content[0]"
    )
    typed.with_uri("file:///x.py")


def test_resource_with_uri_should_raise_when_differs():
    typed = AssertableResourceContent({"type": "resource", "resource": {"uri": "file:///other.py"}}, label="Content[0]")
    with pytest.raises(AssertionError, match="uri"):
        typed.with_uri("file:///x.py")


def test_resource_with_mime_type_should_pass_when_matches():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "mimeType": "text/yaml"}}, label="Content[0]"
    )
    typed.with_mime_type("text/yaml")


def test_resource_with_mime_type_should_raise_when_differs():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "mimeType": "text/plain"}}, label="Content[0]"
    )
    with pytest.raises(AssertionError, match="mimeType"):
        typed.with_mime_type("text/yaml")


def test_resource_with_text_should_pass_when_matches():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "text": "debug: true"}}, label="Content[0]"
    )
    typed.with_text("debug: true")


def test_resource_with_text_should_raise_when_differs():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "text": "other"}}, label="Content[0]"
    )
    with pytest.raises(AssertionError, match="text"):
        typed.with_text("expected")


def test_resource_with_text_should_raise_when_text_field_absent():
    typed = AssertableResourceContent({"type": "resource", "resource": {"uri": "x"}}, label="Content[0]")
    with pytest.raises(AssertionError, match="text"):
        typed.with_text("expected")


def test_resource_with_text_containing_should_pass_when_substring_present():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "text": "def main(): pass"}}, label="Content[0]"
    )
    typed.with_text_containing("def main")


def test_resource_with_text_containing_should_raise_when_substring_absent():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "text": "x = 1"}}, label="Content[0]"
    )
    with pytest.raises(AssertionError, match="does not contain"):
        typed.with_text_containing("def main")


def test_resource_with_blob_data_should_pass_for_valid_base64_blob():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "blob": "aGVsbG8="}}, label="Content[0]"
    )
    typed.with_blob_data()


def test_resource_with_blob_data_should_raise_when_blob_missing():
    typed = AssertableResourceContent({"type": "resource", "resource": {"uri": "x"}}, label="Content[0]")
    with pytest.raises(AssertionError, match="missing or empty"):
        typed.with_blob_data()


def test_resource_with_blob_data_should_raise_when_blob_invalid_base64():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "x", "blob": "%%%not-base64"}}, label="Content[0]"
    )
    with pytest.raises(AssertionError, match="not valid base64"):
        typed.with_blob_data()


def test_text_methods_should_return_self_for_chaining():
    typed = AssertableTextContent({"type": "text", "text": "hello world"}, label="Content[0]")
    result = typed.with_text_containing("hello").with_text_containing("world").is_not_empty()
    assert result is typed


def test_image_methods_should_return_self_for_chaining():
    typed = AssertableImageContent({"type": "image", "mimeType": "image/png", "data": "aGVsbG8="}, label="Content[0]")
    result = typed.with_mime_type("image/png").with_base64_data()
    assert result is typed


def test_resource_methods_should_return_self_for_chaining():
    typed = AssertableResourceContent(
        {"type": "resource", "resource": {"uri": "file:///x", "mimeType": "text/yaml", "text": "k: v"}},
        label="Content[0]",
    )
    result = typed.with_uri("file:///x").with_mime_type("text/yaml").with_text("k: v")
    assert result is typed
