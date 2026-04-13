from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyssertive.http.client import FluentHttpAssertClient
from pyssertive.http.json import AssertableJson

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

SAMPLE = {
    "user": {
        "id": 1,
        "name": "John",
        "profile": {"age": 30, "city": "NYC"},
    },
    "tags": ["python", "django"],
    "count": 42,
}


@pytest.fixture
def doc() -> AssertableJson:
    return AssertableJson(SAMPLE)


VALID_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "user": {"type": "object"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "count": {"type": "integer"},
    },
    "required": ["user", "tags", "count"],
}


def test_matches_schema_should_pass_when_data_conforms(doc: AssertableJson) -> None:
    doc.matches_schema(VALID_SCHEMA)


def test_matches_schema_should_fail_when_required_field_missing() -> None:
    data = {"tags": ["python"]}
    with pytest.raises(AssertionError, match="schema validation failed"):
        AssertableJson(data).matches_schema(VALID_SCHEMA)


def test_matches_schema_should_fail_when_type_mismatches() -> None:
    data = {**SAMPLE, "count": "not_an_int"}
    with pytest.raises(AssertionError, match="schema validation failed"):
        AssertableJson(data).matches_schema(VALID_SCHEMA)


def test_matches_schema_should_report_failing_path() -> None:
    data = {**SAMPLE, "tags": "not_a_list"}
    with pytest.raises(AssertionError, match="'tags'"):
        AssertableJson(data).matches_schema(VALID_SCHEMA)


def test_matches_schema_should_return_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.matches_schema(VALID_SCHEMA) is doc


def test_matches_schema_should_pass_with_str_file_path(doc: AssertableJson) -> None:
    doc.matches_schema(str(SCHEMAS_DIR / "sample_nested.json"))


def test_matches_schema_should_pass_with_path_object(doc: AssertableJson) -> None:
    doc.matches_schema(SCHEMAS_DIR / "sample_nested.json")


def test_matches_schema_should_fail_when_file_not_found(doc: AssertableJson) -> None:
    with pytest.raises(FileNotFoundError, match="Schema file not found"):
        doc.matches_schema("nonexistent/schema.json")


def test_matches_schema_should_fail_when_file_schema_mismatches() -> None:
    data = {"ok": "not_a_bool"}
    with pytest.raises(AssertionError, match="schema validation failed"):
        AssertableJson(data).matches_schema(SCHEMAS_DIR / "sample_ok.json")


def test_matches_schema_should_pass_with_url_schema(doc: AssertableJson) -> None:
    remote_schema = json.dumps(VALID_SCHEMA).encode()
    mock_response = MagicMock()
    mock_response.read.return_value = remote_schema
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("pyssertive.http.json.urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        doc.matches_schema("https://api.example.com/schemas/sample.json")
    mock_urlopen.assert_called_once_with("https://api.example.com/schemas/sample.json")


def test_matches_schema_should_fail_with_url_schema_when_data_invalid() -> None:
    strict_schema = json.dumps(
        {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}
    ).encode()
    mock_response = MagicMock()
    mock_response.read.return_value = strict_schema
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with (
        patch("pyssertive.http.json.urllib.request.urlopen", return_value=mock_response),
        pytest.raises(AssertionError, match="schema validation failed"),
    ):
        AssertableJson({"ok": True}).matches_schema("https://api.example.com/schemas/strict.json")


def test_matches_schema_should_include_scope_in_error_message() -> None:
    user_schema = {
        "type": "object",
        "properties": {"id": {"type": "string"}},
        "required": ["id"],
    }
    scoped = AssertableJson(SAMPLE["user"], _path="user")
    with pytest.raises(AssertionError, match="at scope 'user'"):
        scoped.matches_schema(user_schema)


@pytest.mark.django_db
def test_assert_json_schema_should_pass_with_inline_dict(
    fluent_admin_client: FluentHttpAssertClient,
) -> None:
    schema = {
        "type": "object",
        "properties": {"ok": {"type": "boolean"}},
        "required": ["ok"],
    }
    fluent_admin_client.get("/json/").assert_json_schema(schema)


@pytest.mark.django_db
def test_assert_json_schema_should_pass_with_file_path(
    fluent_admin_client: FluentHttpAssertClient,
) -> None:
    fluent_admin_client.get("/json/").assert_json_schema(SCHEMAS_DIR / "sample_ok.json")


@pytest.mark.django_db
def test_assert_json_schema_should_fail_when_response_mismatches(
    fluent_admin_client: FluentHttpAssertClient,
) -> None:
    wrong_schema = {
        "type": "object",
        "properties": {"id": {"type": "integer"}},
        "required": ["id"],
    }
    with pytest.raises(AssertionError, match="schema validation failed"):
        fluent_admin_client.get("/json/").assert_json_schema(wrong_schema)


@pytest.mark.django_db
def test_assert_json_schema_should_return_self_for_chaining(
    fluent_admin_client: FluentHttpAssertClient,
) -> None:
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    response = fluent_admin_client.get("/json/")
    assert response.assert_json_schema(schema) is response


@pytest.mark.django_db
def test_assert_json_schema_should_chain_with_other_assertions(
    fluent_admin_client: FluentHttpAssertClient,
) -> None:
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    fluent_admin_client.get("/json/").assert_ok().assert_json_schema(schema).assert_json_path("ok", True)


@pytest.mark.django_db
def test_assert_json_schema_should_pass_with_nested_response(
    fluent_admin_client: FluentHttpAssertClient,
) -> None:
    fluent_admin_client.get("/json-nested/").assert_json_schema(SCHEMAS_DIR / "sample_nested.json")
