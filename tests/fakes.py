from typing import Any, Dict
from contextlib import contextmanager
import importlib
import sys
import types


class FakeMockServiceClient:
    def __init__(self):
        self.paths = []
        self.ticket_ids = []
        self.build_ids = []
        self.doc_slugs = []

    def get_json(self, path: str) -> Dict[str, Any]:
        self.paths.append(path)
        if path == "/health":
            return {"ok": True, "service": "stack-sentinel-mock-api"}
        return {"ok": False, "error": "unexpected path"}

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        self.ticket_ids.append(ticket_id)
        if ticket_id == "TCK-101":
            return {
                "ok": True,
                "data": {
                    "id": "TCK-101",
                    "summary": "Usuarios relatam erro 500 ao tentar login no portal.",
                    "severity": "high",
                    "service": "auth-service",
                    "status": "open",
                    "build_id": "BLD-203",
                    "title": "Erro 500 no login do portal",
                },
            }
        return {"ok": False, "error": "not found"}

    def get_build(self, build_id: str) -> Dict[str, Any]:
        self.build_ids.append(build_id)
        if build_id == "BLD-203":
            return {
                "ok": True,
                "data": {
                    "id": "BLD-203",
                    "status": "failed",
                    "service": "auth-service",
                    "branch": "main",
                    "failed_step": "integration-tests",
                    "log_excerpt": "test_login_with_mfa returned HTTP 500 instead of 200",
                },
            }
        return {"ok": False, "error": "not found"}

    def get_doc(self, slug: str) -> Dict[str, Any]:
        self.doc_slugs.append(slug)
        docs = {
            "incident-response": {
                "slug": "incident-response",
                "title": "Incident Response Guide",
                "content": "Identifique impacto, severidade, evidencias e proximo passo.",
            },
            "severity-policy": {
                "slug": "severity-policy",
                "title": "Severity Policy",
                "content": "critical, high, medium, low",
            },
        }
        if slug in docs:
            return {"ok": True, "data": docs[slug]}
        return {"ok": False, "error": "not found"}


class BrokenMockServiceClient(FakeMockServiceClient):
    def get_json(self, path: str) -> Dict[str, Any]:
        self.paths.append(path)
        return {"ok": False, "error": "service unavailable"}


class FakeFastMCP:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.prompts = {}

    def tool(self, func=None):
        def decorator(handler):
            self.tools[handler.__name__] = handler
            return handler

        if func is not None:
            return decorator(func)
        return decorator

    def resource(self, uri: str):
        def decorator(handler):
            self.resources[uri] = handler
            return handler

        return decorator

    def prompt(self, func=None):
        def decorator(handler):
            self.prompts[handler.__name__] = handler
            return handler

        if func is not None:
            return decorator(func)
        return decorator

    def run(self):
        return None

    def list_tools(self):
        return [{"name": name, "description": handler.__doc__ or ""} for name, handler in self.tools.items()]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            return {"ok": False, "error": f"unknown tool: {name}"}
        return self.tools[name](**arguments)

    def list_resources(self):
        return [{"uri": uri, "name": uri, "description": ""} for uri in self.resources]

    def read_resource(self, uri: str) -> Dict[str, Any]:
        if uri not in self.resources:
            return {"ok": False, "error": f"unknown resource: {uri}"}
        return self.resources[uri]()

    def list_prompts(self):
        return [{"name": name, "description": handler.__doc__ or ""} for name, handler in self.prompts.items()]

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.prompts:
            return {"ok": False, "error": f"unknown prompt: {name}"}
        return {"ok": True, "name": name, "content": self.prompts[name](**arguments)}


def install_fake_fastmcp() -> None:
    """Instala um modulo mcp.server.fastmcp fake para testes deterministico."""
    mcp_module = types.ModuleType("mcp")
    server_module = types.ModuleType("mcp.server")
    fastmcp_module = types.ModuleType("mcp.server.fastmcp")
    fastmcp_module.FastMCP = FakeFastMCP
    server_module.fastmcp = fastmcp_module
    mcp_module.server = server_module
    sys.modules["mcp"] = mcp_module
    sys.modules["mcp.server"] = server_module
    sys.modules["mcp.server.fastmcp"] = fastmcp_module


@contextmanager
def fastmcp_test_client():
    from stack_sentinel.clients.mcp_client import MCPClient
    from stack_sentinel.mcp_server import resources as resources_module
    from stack_sentinel.mcp_server import tools as tools_module

    install_fake_fastmcp()
    sys.modules.pop("stack_sentinel.mcp_server.fastmcp_server", None)
    fastmcp_server = importlib.import_module("stack_sentinel.mcp_server.fastmcp_server")

    original_tools_client = tools_module.MockServiceClient
    original_resources_client = resources_module.MockServiceClient
    tools_module.MockServiceClient = FakeMockServiceClient
    resources_module.MockServiceClient = FakeMockServiceClient
    try:
        yield MCPClient(fastmcp_server.create_fastmcp_server())
    finally:
        tools_module.MockServiceClient = original_tools_client
        resources_module.MockServiceClient = original_resources_client
