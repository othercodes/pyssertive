from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from pyssertive.http.request import RequestBuilder
from pyssertive.protocols.mcp.assertable import AssertableMCP

TBuilt = TypeVar("TBuilt")


class MCPAssertionsMixin:
    _response: Any

    @overload
    def assert_mcp(self) -> AssertableMCP: ...

    @overload
    def assert_mcp(self, callback: Callable[[AssertableMCP], Any]) -> Self: ...

    def assert_mcp(self, callback: Callable[[AssertableMCP], Any] | None = None) -> AssertableMCP | Self:
        assertable = AssertableMCP(self._response)
        if callback is None:
            return assertable
        callback(assertable)
        return self


class MessageBuilder(Generic[TBuilt]):
    DEFAULT_PATH = "/mcp"

    def __init__(self, request_builder: RequestBuilder[TBuilt], *, path: str = DEFAULT_PATH) -> None:
        self._rb = request_builder
        self._rb.with_method("POST")
        self._rb.with_path(path)
        self._rb.with_header("Content-Type", "application/json")
        self._rb.with_header("Accept", "application/json, text/event-stream")

        self._method: str | None = None
        self._params: dict[str, Any] | None = None
        self._id: int | str = 1
        self._is_notification: bool = False

    def with_id(self, msg_id: int | str) -> Self:
        if self._is_notification:
            raise ValueError("Notifications cannot have an id")
        self._id = msg_id
        return self

    def with_auth_token(self, token: str) -> Self:
        self._rb.with_header("Authorization", f"Token {token}")
        return self

    def with_protocol_version(self, version: str) -> Self:
        self._rb.with_header("MCP-Protocol-Version", version)
        return self

    def with_session_id(self, session_id: str) -> Self:
        self._rb.with_header("MCP-Session-Id", session_id)
        return self

    def initialize(
        self,
        *,
        protocol: str = "2025-11-25",
        client_name: str = "pyssertive-test",
        client_version: str = "0.0.0",
        capabilities: dict[str, Any] | None = None,
    ) -> Self:
        self._is_notification = False
        self._method = "initialize"
        self._params = {
            "protocolVersion": protocol,
            "clientInfo": {"name": client_name, "version": client_version},
            "capabilities": capabilities if capabilities is not None else {},
        }
        return self

    def listing_tools(self, *, cursor: str | None = None) -> Self:
        return self._set_listing("tools/list", cursor)

    def calling_tool(self, name: str, *, arguments: dict[str, Any] | None = None) -> Self:
        self._is_notification = False
        self._method = "tools/call"
        self._params = {"name": name, "arguments": arguments if arguments is not None else {}}
        return self

    def listing_resources(self, *, cursor: str | None = None) -> Self:
        return self._set_listing("resources/list", cursor)

    def reading_resource(self, uri: str) -> Self:
        self._is_notification = False
        self._method = "resources/read"
        self._params = {"uri": uri}
        return self

    def listing_prompts(self, *, cursor: str | None = None) -> Self:
        return self._set_listing("prompts/list", cursor)

    def getting_prompt(self, name: str, *, arguments: dict[str, Any] | None = None) -> Self:
        self._is_notification = False
        self._method = "prompts/get"
        self._params = {"name": name, "arguments": arguments if arguments is not None else {}}
        return self

    def notifying(self, method: str, *, params: dict[str, Any] | None = None) -> Self:
        self._is_notification = True
        self._method = method
        self._params = params
        return self

    def calling(self, method: str) -> Self:
        self._is_notification = False
        self._method = method
        self._params = None
        return self

    def with_params(self, params: dict[str, Any]) -> Self:
        self._params = params
        return self

    def build(self) -> TBuilt:
        if self._method is None:
            raise ValueError("Cannot build MCP message: no method set")

        envelope: dict[str, Any] = {"jsonrpc": "2.0"}
        if not self._is_notification:
            envelope["id"] = self._id
        envelope["method"] = self._method

        if self._is_notification:
            if self._params is not None:
                envelope["params"] = self._params
        else:
            envelope["params"] = self._params if self._params is not None else {}

        self._rb.with_body(envelope)
        return self._rb.build()

    def _set_listing(self, method: str, cursor: str | None) -> Self:
        self._is_notification = False
        self._method = method
        self._params = {"cursor": cursor} if cursor is not None else {}
        return self
