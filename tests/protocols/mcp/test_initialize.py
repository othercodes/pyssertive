from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _init_response(
    *,
    protocol: str = "2024-11-05",
    server_name: str = "webshare",
    server_version: str = "1.0.0",
    capabilities: dict | None = None,
    instructions: str | None = None,
) -> dict:
    result = {
        "protocolVersion": protocol,
        "serverInfo": {"name": server_name, "version": server_version},
        "capabilities": capabilities if capabilities is not None else {"tools": {}},
    }
    if instructions is not None:
        result["instructions"] = instructions
    return {"jsonrpc": "2.0", "id": 1, "result": result}


def test_negotiated_protocol_should_pass_when_version_matches():
    AssertableMCP(_init_response(protocol="2025-11-25")).negotiated_protocol("2025-11-25")


def test_negotiated_protocol_should_raise_when_version_differs():
    with pytest.raises(AssertionError, match="protocolVersion"):
        AssertableMCP(_init_response(protocol="2024-11-05")).negotiated_protocol("2025-11-25")


def test_server_named_should_pass_when_name_matches():
    AssertableMCP(_init_response(server_name="my-server")).server_named("my-server")


def test_server_named_should_raise_when_name_differs():
    with pytest.raises(AssertionError, match=r"serverInfo\.name"):
        AssertableMCP(_init_response(server_name="other")).server_named("expected")


def test_server_version_should_pass_when_version_matches():
    AssertableMCP(_init_response(server_version="2.3.4")).server_version("2.3.4")


def test_server_version_should_raise_when_version_differs():
    with pytest.raises(AssertionError, match=r"serverInfo\.version"):
        AssertableMCP(_init_response(server_version="2.3.4")).server_version("9.9.9")


def test_supports_tools_should_pass_when_capability_present():
    AssertableMCP(_init_response(capabilities={"tools": {}})).supports_tools()


def test_supports_tools_should_raise_when_capability_absent():
    with pytest.raises(AssertionError, match="'tools' capability"):
        AssertableMCP(_init_response(capabilities={"resources": {}})).supports_tools()


def test_supports_resources_should_pass_when_capability_present():
    AssertableMCP(_init_response(capabilities={"resources": {}})).supports_resources()


def test_supports_resources_should_pass_when_subscribe_flag_matches():
    response = _init_response(capabilities={"resources": {"subscribe": True}})
    AssertableMCP(response).supports_resources(subscribe=True)


def test_supports_resources_should_raise_when_subscribe_flag_differs():
    response = _init_response(capabilities={"resources": {"subscribe": False}})
    with pytest.raises(AssertionError, match=r"resources\.subscribe"):
        AssertableMCP(response).supports_resources(subscribe=True)


def test_supports_resources_should_raise_when_capability_absent():
    with pytest.raises(AssertionError, match="'resources' capability"):
        AssertableMCP(_init_response(capabilities={"tools": {}})).supports_resources()


def test_supports_prompts_should_pass_when_capability_present():
    AssertableMCP(_init_response(capabilities={"prompts": {}})).supports_prompts()


def test_supports_prompts_should_raise_when_capability_absent():
    with pytest.raises(AssertionError, match="'prompts' capability"):
        AssertableMCP(_init_response(capabilities={})).supports_prompts()


def test_supports_logging_should_pass_when_capability_present():
    AssertableMCP(_init_response(capabilities={"logging": {}})).supports_logging()


def test_supports_logging_should_raise_when_capability_absent():
    with pytest.raises(AssertionError, match="'logging' capability"):
        AssertableMCP(_init_response(capabilities={})).supports_logging()


def test_has_instructions_should_pass_when_instructions_field_set():
    AssertableMCP(_init_response(instructions="hello operator")).has_instructions()


def test_has_instructions_should_raise_when_instructions_field_absent():
    with pytest.raises(AssertionError, match="no instructions"):
        AssertableMCP(_init_response()).has_instructions()


def test_assertable_should_chain_initialize_assertions():
    response = _init_response(
        protocol="2024-11-05",
        server_name="webshare",
        server_version="1.0.0",
        capabilities={"tools": {}, "resources": {"subscribe": True}, "prompts": {}, "logging": {}},
        instructions="ok",
    )
    chain = (
        AssertableMCP(response)
        .negotiated_protocol("2024-11-05")
        .server_named("webshare")
        .server_version("1.0.0")
        .supports_tools()
        .supports_resources(subscribe=True)
        .supports_prompts()
        .supports_logging()
        .has_instructions()
    )
    assert isinstance(chain, AssertableMCP)


def test_assertable_should_raise_when_result_missing_on_initialize_chain():
    payload = {"jsonrpc": "2.0", "id": 1, "error": {"code": -1, "message": "boom"}}
    with pytest.raises(AssertionError, match="error"):
        AssertableMCP(payload).negotiated_protocol("any")


def test_assertable_should_raise_when_result_is_not_object():
    payload = {"jsonrpc": "2.0", "id": 1, "result": "boom"}
    with pytest.raises(AssertionError, match="not an object"):
        AssertableMCP(payload).negotiated_protocol("any")


def test_assertable_should_raise_when_capabilities_missing_object():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "x"}}
    with pytest.raises(AssertionError, match="capabilities"):
        AssertableMCP(payload).supports_tools()
