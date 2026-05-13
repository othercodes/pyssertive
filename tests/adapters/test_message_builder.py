from __future__ import annotations

import json
from typing import Any, cast

import pytest

from pyssertive.http.mcp import MessageBuilder
from tests.adapters._factories import REQUEST_BUILDER_ADAPTERS, inspect


def _decode_envelope(body: Any) -> dict[str, Any]:
    if isinstance(body, bytes):
        return cast(dict[str, Any], json.loads(body.decode("utf-8")))
    if isinstance(body, str):
        return cast(dict[str, Any], json.loads(body))
    if isinstance(body, dict):
        return body
    raise AssertionError(f"Unsupported body shape: {type(body).__name__}")


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_message_builder_should_post_to_default_mcp_path(builder_cls):
    snapshot = inspect(MessageBuilder(builder_cls()).calling_tool("ping").build())
    assert snapshot["method"] == "POST"
    assert snapshot["path"] == "/mcp"


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_message_builder_should_accept_custom_path(builder_cls):
    snapshot = inspect(MessageBuilder(builder_cls(), path="/v1/mcp").calling_tool("ping").build())
    assert snapshot["path"] == "/v1/mcp"


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_message_builder_should_set_jsonrpc_content_type_and_accept_headers(builder_cls):
    snapshot = inspect(MessageBuilder(builder_cls()).calling_tool("ping").build())
    assert snapshot["headers"].get("content-type", "").startswith("application/json")
    accept = snapshot["headers"].get("accept", "")
    assert "application/json" in accept and "text/event-stream" in accept


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_initialize_should_build_handshake_envelope_with_defaults(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).initialize().build())["body"])
    assert envelope["jsonrpc"] == "2.0"
    assert envelope["id"] == 1
    assert envelope["method"] == "initialize"
    assert envelope["params"]["protocolVersion"] == "2025-11-25"
    assert envelope["params"]["clientInfo"]["name"] == "pyssertive-test"
    assert envelope["params"]["capabilities"] == {}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_initialize_should_accept_overrides(builder_cls):
    envelope = _decode_envelope(
        inspect(
            MessageBuilder(builder_cls())
            .initialize(
                protocol="2024-11-05",
                client_name="my-client",
                client_version="9.9.9",
                capabilities={"sampling": {}},
            )
            .build()
        )["body"]
    )
    assert envelope["params"]["protocolVersion"] == "2024-11-05"
    assert envelope["params"]["clientInfo"] == {"name": "my-client", "version": "9.9.9"}
    assert envelope["params"]["capabilities"] == {"sampling": {}}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_listing_tools_should_build_tools_list_envelope(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).listing_tools().build())["body"])
    assert envelope["method"] == "tools/list"
    assert envelope["params"] == {}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_listing_tools_should_include_cursor_when_provided(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).listing_tools(cursor="abc").build())["body"])
    assert envelope["params"] == {"cursor": "abc"}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_calling_tool_should_build_tools_call_envelope(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).calling_tool("get_weather", arguments={"location": "Madrid"}).build())[
            "body"
        ]
    )
    assert envelope["method"] == "tools/call"
    assert envelope["params"] == {"name": "get_weather", "arguments": {"location": "Madrid"}}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_calling_tool_should_default_arguments_to_empty_object(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).calling_tool("ping").build())["body"])
    assert envelope["params"] == {"name": "ping", "arguments": {}}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_listing_resources_should_build_resources_list_envelope(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).listing_resources(cursor="next").build())["body"])
    assert envelope["method"] == "resources/list"
    assert envelope["params"] == {"cursor": "next"}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_reading_resource_should_build_resources_read_envelope(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).reading_resource("file:///main.py").build())["body"]
    )
    assert envelope["method"] == "resources/read"
    assert envelope["params"] == {"uri": "file:///main.py"}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_listing_prompts_should_build_prompts_list_envelope(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).listing_prompts().build())["body"])
    assert envelope["method"] == "prompts/list"
    assert envelope["params"] == {}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_getting_prompt_should_build_prompts_get_envelope(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).getting_prompt("code_review", arguments={"lang": "python"}).build())[
            "body"
        ]
    )
    assert envelope["method"] == "prompts/get"
    assert envelope["params"] == {"name": "code_review", "arguments": {"lang": "python"}}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_notifying_should_build_notification_envelope_without_id(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).notifying("notifications/initialized").build())["body"]
    )
    assert envelope["jsonrpc"] == "2.0"
    assert envelope["method"] == "notifications/initialized"
    assert "id" not in envelope


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_notifying_should_include_params_when_provided(builder_cls):
    envelope = _decode_envelope(
        inspect(
            MessageBuilder(builder_cls())
            .notifying("notifications/progress", params={"progress": 50, "total": 100})
            .build()
        )["body"]
    )
    assert envelope["params"] == {"progress": 50, "total": 100}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_notifying_should_omit_params_field_when_not_provided(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).notifying("notifications/initialized").build())["body"]
    )
    assert "params" not in envelope


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_calling_low_level_should_build_arbitrary_method_envelope(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).calling("logging/setLevel").with_params({"level": "debug"}).build())[
            "body"
        ]
    )
    assert envelope["method"] == "logging/setLevel"
    assert envelope["params"] == {"level": "debug"}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_calling_low_level_should_default_params_to_empty_object(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).calling("ping").build())["body"])
    assert envelope["params"] == {}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_with_id_should_override_default_request_id(builder_cls):
    envelope = _decode_envelope(inspect(MessageBuilder(builder_cls()).calling_tool("x").with_id(42).build())["body"])
    assert envelope["id"] == 42


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_with_id_should_accept_string_ids(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).calling_tool("x").with_id("req-uuid").build())["body"]
    )
    assert envelope["id"] == "req-uuid"


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_with_id_should_raise_when_applied_to_notification(builder_cls):
    with pytest.raises(ValueError, match="Notifications cannot have an id"):
        MessageBuilder(builder_cls()).notifying("notifications/initialized").with_id(1)


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_build_should_raise_when_no_method_configured(builder_cls):
    with pytest.raises(ValueError, match="no method set"):
        MessageBuilder(builder_cls()).build()


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_calling_should_reset_params_when_overriding_high_level_shortcut(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).calling_tool("x").calling("custom/method").with_params({"y": 1}).build())[
            "body"
        ]
    )
    assert envelope["method"] == "custom/method"
    assert envelope["params"] == {"y": 1}


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_with_auth_token_should_set_authorization_header(builder_cls):
    snapshot = inspect(MessageBuilder(builder_cls()).with_auth_token("abc123").calling_tool("ping").build())
    assert snapshot["headers"].get("authorization") == "Token abc123"


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_with_protocol_version_should_set_mcp_protocol_version_header(builder_cls):
    snapshot = inspect(MessageBuilder(builder_cls()).with_protocol_version("2024-11-05").calling_tool("ping").build())
    assert snapshot["headers"].get("mcp-protocol-version") == "2024-11-05"


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_with_session_id_should_set_mcp_session_id_header(builder_cls):
    snapshot = inspect(MessageBuilder(builder_cls()).with_session_id("sess-xyz").calling_tool("ping").build())
    assert snapshot["headers"].get("mcp-session-id") == "sess-xyz"


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_notifying_should_clear_id_even_when_previously_set(builder_cls):
    envelope = _decode_envelope(
        inspect(
            MessageBuilder(builder_cls()).with_id(99).calling_tool("x").notifying("notifications/initialized").build()
        )["body"]
    )
    assert "id" not in envelope


@pytest.mark.parametrize("builder_cls", REQUEST_BUILDER_ADAPTERS)
def test_message_builder_should_emit_full_envelope(builder_cls):
    envelope = _decode_envelope(
        inspect(MessageBuilder(builder_cls()).calling_tool("get_weather", arguments={"location": "Madrid"}).build())[
            "body"
        ]
    )
    assert envelope == {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_weather", "arguments": {"location": "Madrid"}},
    }
