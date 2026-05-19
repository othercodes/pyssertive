from __future__ import annotations

import pytest

from pyssertive.protocols.mcp.content import AssertableContent


@pytest.mark.parametrize(
    ("guard", "block"),
    [
        ("is_text", {"type": "text", "text": "hi"}),
        ("is_image", {"type": "image", "mimeType": "image/png", "data": "Zm9v"}),
        ("is_audio", {"type": "audio", "mimeType": "audio/mpeg", "data": "Zm9v"}),
        ("is_resource_link", {"type": "resource_link", "uri": "file:///x"}),
        ("is_resource", {"type": "resource", "resource": {"uri": "file:///x"}}),
    ],
    ids=["text", "image", "audio", "resource_link", "resource"],
)
def test_type_guard_should_pass_for_matching_type(guard, block):
    result = getattr(AssertableContent(block, label="Content[0]"), guard)()
    assert isinstance(result, AssertableContent)


@pytest.mark.parametrize(
    ("guard", "wrong_block"),
    [
        ("is_text", {"type": "image"}),
        ("is_image", {"type": "text"}),
        ("is_audio", {"type": "text"}),
        ("is_resource_link", {"type": "resource"}),
        ("is_resource", {"type": "resource_link"}),
    ],
    ids=[
        "is_text_on_image",
        "is_image_on_text",
        "is_audio_on_text",
        "is_resource_link_on_resource",
        "is_resource_on_resource_link",
    ],
)
def test_type_guard_should_raise_when_block_is_wrong_type(guard, wrong_block):
    with pytest.raises(AssertionError, match="expected"):
        getattr(AssertableContent(wrong_block, label="Content[0]"), guard)()


def test_type_guard_should_raise_when_block_is_not_a_dict():
    with pytest.raises(AssertionError, match="not a dict"):
        AssertableContent("not-a-dict", label="Content[0]").is_text()


def test_type_guard_should_mention_unknown_type_when_type_field_absent():
    with pytest.raises(AssertionError, match="'<unknown>'"):
        AssertableContent({}, label="Content[0]").is_text()


def test_type_guard_should_treat_non_string_type_as_unknown():
    with pytest.raises(AssertionError, match="'<unknown>'"):
        AssertableContent({"type": 42}, label="Content[0]").is_text()


def test_with_text_should_pass_on_text_block():
    AssertableContent({"type": "text", "text": "hi"}, label="Content[0]").with_text("hi")


def test_with_text_should_pass_on_resource_block_with_embedded_text():
    AssertableContent({"type": "resource", "resource": {"uri": "x", "text": "hi"}}, label="Content[0]").with_text("hi")


def test_with_text_should_raise_when_text_differs_on_text_block():
    with pytest.raises(AssertionError, match="expected 'xyz'"):
        AssertableContent({"type": "text", "text": "abc"}, label="Content[0]").with_text("xyz")


def test_with_text_should_raise_when_text_differs_on_resource_block():
    with pytest.raises(AssertionError, match="expected 'xyz'"):
        AssertableContent({"type": "resource", "resource": {"uri": "x", "text": "abc"}}, label="Content[0]").with_text(
            "xyz"
        )


def test_with_text_should_raise_when_block_type_does_not_carry_text():
    with pytest.raises(AssertionError, match=r"with_text\(\) requires type"):
        AssertableContent({"type": "image", "data": "Zm9v"}, label="Content[0]").with_text("hi")


def test_with_text_containing_should_pass_when_substring_present():
    AssertableContent({"type": "text", "text": "hello world"}, label="Content[0]").with_text_containing("world")


def test_with_text_containing_should_pass_on_resource_block():
    AssertableContent(
        {"type": "resource", "resource": {"uri": "x", "text": "def main(): pass"}}, label="Content[0]"
    ).with_text_containing("def main")


def test_with_text_containing_should_raise_when_substring_absent():
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableContent({"type": "text", "text": "hello"}, label="Content[0]").with_text_containing("missing")


def test_with_text_containing_should_raise_for_wrong_type():
    with pytest.raises(AssertionError, match=r"with_text_containing\(\) requires type"):
        AssertableContent({"type": "image"}, label="Content[0]").with_text_containing("anything")


@pytest.mark.parametrize(
    "block",
    [
        {"type": "text", "text": "hi"},
        {"type": "resource", "resource": {"uri": "x", "text": "hi"}},
        {"type": "resource", "resource": {"uri": "x", "blob": "Zm9v"}},
        {"type": "image", "data": "Zm9v"},
        {"type": "audio", "data": "Zm9v"},
    ],
    ids=["text", "resource_with_text", "resource_with_blob", "image", "audio"],
)
def test_is_not_empty_should_pass_when_payload_present(block):
    AssertableContent(block, label="Content[0]").is_not_empty()


@pytest.mark.parametrize(
    "block",
    [
        {"type": "text", "text": ""},
        {"type": "text"},
        {"type": "resource", "resource": {"uri": "x"}},
        {"type": "image", "data": ""},
        {"type": "image"},
        {"type": "audio", "data": ""},
    ],
    ids=[
        "text_empty",
        "text_absent",
        "resource_no_payload",
        "image_data_empty",
        "image_data_absent",
        "audio_data_empty",
    ],
)
def test_is_not_empty_should_raise_when_payload_missing(block):
    with pytest.raises(AssertionError, match="empty"):
        AssertableContent(block, label="Content[0]").is_not_empty()


def test_is_not_empty_should_raise_when_payload_is_not_a_string():
    with pytest.raises(AssertionError, match="empty"):
        AssertableContent({"type": "text", "text": 42}, label="Content[0]").is_not_empty()


def test_is_not_empty_should_raise_for_wrong_type():
    with pytest.raises(AssertionError, match=r"is_not_empty\(\) requires type"):
        AssertableContent({"type": "resource_link", "uri": "x"}, label="Content[0]").is_not_empty()


@pytest.mark.parametrize(
    ("block", "expected"),
    [
        ({"type": "image", "mimeType": "image/png", "data": "Zm9v"}, "image/png"),
        ({"type": "audio", "mimeType": "audio/mpeg", "data": "Zm9v"}, "audio/mpeg"),
        ({"type": "resource_link", "uri": "x", "mimeType": "text/x-python"}, "text/x-python"),
        ({"type": "resource", "resource": {"uri": "x", "mimeType": "text/yaml"}}, "text/yaml"),
    ],
    ids=["image", "audio", "resource_link", "embedded_resource"],
)
def test_with_mime_type_should_pass_for_compatible_types(block, expected):
    AssertableContent(block, label="Content[0]").with_mime_type(expected)


@pytest.mark.parametrize(
    "block",
    [
        {"type": "image", "mimeType": "image/jpeg"},
        {"type": "image", "data": "Zm9v"},
    ],
    ids=["differs", "absent"],
)
def test_with_mime_type_should_raise_when_value_does_not_match(block):
    with pytest.raises(AssertionError, match="mimeType"):
        AssertableContent(block, label="Content[0]").with_mime_type("image/png")


def test_with_mime_type_should_raise_on_text_block():
    with pytest.raises(AssertionError, match=r"with_mime_type\(\) requires type"):
        AssertableContent({"type": "text", "text": "hi"}, label="Content[0]").with_mime_type("text/plain")


def test_with_base64_data_should_pass_for_valid_image_data():
    AssertableContent({"type": "image", "data": "aGVsbG8="}, label="Content[0]").with_base64_data()


def test_with_base64_data_should_pass_for_valid_audio_data():
    AssertableContent({"type": "audio", "data": "aGVsbG8="}, label="Content[0]").with_base64_data()


def test_with_base64_data_should_raise_when_data_missing():
    with pytest.raises(AssertionError, match="missing or empty"):
        AssertableContent({"type": "image", "data": ""}, label="Content[0]").with_base64_data()


def test_with_base64_data_should_raise_when_data_invalid():
    with pytest.raises(AssertionError, match="not valid base64"):
        AssertableContent({"type": "image", "data": "%%%nope"}, label="Content[0]").with_base64_data()


def test_with_base64_data_should_raise_for_wrong_type():
    with pytest.raises(AssertionError, match=r"with_base64_data\(\) requires type"):
        AssertableContent({"type": "resource", "resource": {"uri": "x"}}, label="Content[0]").with_base64_data()


def test_with_blob_data_should_pass_for_valid_blob():
    AssertableContent(
        {"type": "resource", "resource": {"uri": "x", "blob": "aGVsbG8="}}, label="Content[0]"
    ).with_blob_data()


def test_with_blob_data_should_raise_when_blob_missing():
    with pytest.raises(AssertionError, match="missing or empty"):
        AssertableContent({"type": "resource", "resource": {"uri": "x"}}, label="Content[0]").with_blob_data()


def test_with_blob_data_should_raise_when_blob_invalid_base64():
    with pytest.raises(AssertionError, match="not valid base64"):
        AssertableContent(
            {"type": "resource", "resource": {"uri": "x", "blob": "%%%nope"}}, label="Content[0]"
        ).with_blob_data()


def test_with_blob_data_should_raise_for_wrong_type():
    with pytest.raises(AssertionError, match=r"with_blob_data\(\) requires type"):
        AssertableContent({"type": "image", "data": "Zm9v"}, label="Content[0]").with_blob_data()


@pytest.mark.parametrize(
    "block",
    [
        {"type": "resource_link", "uri": "file:///main.py"},
        {"type": "resource", "resource": {"uri": "file:///main.py"}},
    ],
    ids=["resource_link", "embedded_resource"],
)
def test_with_uri_should_pass_on_compatible_types(block):
    AssertableContent(block, label="Content[0]").with_uri("file:///main.py")


@pytest.mark.parametrize(
    "block",
    [
        {"type": "resource_link", "uri": "file:///wrong"},
        {"type": "resource_link"},
        {"type": "resource", "resource": {"uri": "file:///wrong"}},
        {"type": "resource", "resource": {}},
    ],
    ids=["link_differs", "link_absent", "embedded_differs", "embedded_absent"],
)
def test_with_uri_should_raise_when_value_does_not_match(block):
    with pytest.raises(AssertionError, match="uri"):
        AssertableContent(block, label="Content[0]").with_uri("file:///right")


def test_with_uri_should_raise_for_wrong_type():
    with pytest.raises(AssertionError, match=r"with_uri\(\) requires type"):
        AssertableContent({"type": "text", "text": "hi"}, label="Content[0]").with_uri("file:///x")


@pytest.mark.parametrize(
    "block",
    [
        {"type": "resource_link", "uri": "x", "name": "main.py"},
        {"type": "resource", "resource": {"uri": "x", "name": "main.py"}},
    ],
    ids=["resource_link", "embedded_resource"],
)
def test_named_should_pass_when_name_matches(block):
    AssertableContent(block, label="Content[0]").named("main.py")


@pytest.mark.parametrize(
    "block",
    [
        {"type": "resource_link", "uri": "x", "name": "other.py"},
        {"type": "resource", "resource": {"uri": "x", "name": "other.py"}},
    ],
    ids=["resource_link", "embedded_resource"],
)
def test_named_should_raise_when_name_differs(block):
    with pytest.raises(AssertionError, match="name"):
        AssertableContent(block, label="Content[0]").named("main.py")


@pytest.mark.parametrize(
    "block",
    [
        {"type": "resource_link", "uri": "x"},
        {"type": "resource", "resource": {"uri": "x"}},
    ],
    ids=["resource_link", "embedded_resource"],
)
def test_named_should_raise_when_name_field_absent(block):
    with pytest.raises(AssertionError, match="name"):
        AssertableContent(block, label="Content[0]").named("main.py")


def test_named_should_raise_for_wrong_type():
    with pytest.raises(AssertionError, match=r"named\(\) requires type"):
        AssertableContent({"type": "text", "text": "hi"}, label="Content[0]").named("main.py")


def test_resource_methods_should_raise_when_resource_field_absent():
    with pytest.raises(AssertionError, match="resource is not a dict"):
        AssertableContent({"type": "resource"}, label="Content[0]").with_uri("file:///x")


def test_resource_methods_should_raise_when_resource_field_is_not_a_dict():
    with pytest.raises(AssertionError, match="resource is not a dict"):
        AssertableContent({"type": "resource", "resource": "not-a-dict"}, label="Content[0]").with_uri("file:///x")


def test_methods_should_return_self_for_chaining():
    block = {"type": "resource", "resource": {"uri": "file:///x", "mimeType": "text/yaml", "text": "k: v"}}
    typed = AssertableContent(block, label="Content[0]")
    result = typed.is_resource().with_uri("file:///x").with_mime_type("text/yaml").with_text("k: v")
    assert result is typed


def test_label_should_appear_in_error_messages():
    with pytest.raises(AssertionError, match=r"Tool 'foo' content\[3\] is of type 'image', expected 'text'"):
        AssertableContent({"type": "image"}, label="Tool 'foo' content[3]").is_text()
