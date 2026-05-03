import asyncio
import inspect
import json
from typing import Any, Dict


class MCPClient:
    """Cliente MCP em memoria para o servidor usado no lab.

    Nos testes, o servidor pode ser um FastMCP fake. Em demos locais, ele pode
    ser o objeto criado por `create_fastmcp_server()`, desde que exponha os
    metodos de listagem/chamada usados aqui.
    """

    def __init__(self, server: Any):
        self.server = server

    def _resolve(self, value: Any) -> Any:
        if inspect.isawaitable(value):
            return asyncio.run(value)
        return value

    def _normalize_tool_result(self, value: Any) -> Dict[str, Any]:
        value = self._resolve(value)
        if isinstance(value, dict):
            return value
        if isinstance(value, list) and value:
            text = getattr(value[0], "text", None) or getattr(value[0], "content", None)
            if text is not None:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"ok": True, "content": text}
        return {"ok": False, "error": "unsupported tool response"}

    def _normalize_resource_result(self, value: Any) -> Dict[str, Any]:
        return self._normalize_tool_result(value)

    def _normalize_prompt_result(self, value: Any, name: str) -> Dict[str, Any]:
        value = self._resolve(value)
        if isinstance(value, dict):
            return value
        messages = getattr(value, "messages", None)
        if messages:
            parts = []
            for message in messages:
                content = getattr(message, "content", None)
                text = getattr(content, "text", None)
                if text:
                    parts.append(text)
            return {"ok": True, "name": name, "content": "\n".join(parts)}
        if isinstance(value, str):
            return {"ok": True, "name": name, "content": value}
        return {"ok": False, "error": "unsupported prompt response"}

    def list_tools(self):
        return self._resolve(self.server.list_tools())

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._normalize_tool_result(self.server.call_tool(name, arguments))

    def list_resources(self):
        return self._resolve(self.server.list_resources())

    def read_resource(self, uri: str) -> Dict[str, Any]:
        return self._normalize_resource_result(self.server.read_resource(uri))

    def list_prompts(self):
        return self._resolve(self.server.list_prompts())

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._normalize_prompt_result(self.server.get_prompt(name, arguments), name)


def create_fastmcp_client() -> MCPClient:
    from stack_sentinel.mcp_server.fastmcp_server import create_fastmcp_server

    return MCPClient(create_fastmcp_server())
