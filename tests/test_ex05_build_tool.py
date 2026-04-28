import importlib
import sys
import unittest

from stack_sentinel.mcp_server import tools as tool_module
from stack_sentinel.mcp_server.tools import fetch_build_status
from stack_sentinel.shared.contracts import BUILD_TOOL_NAME
from tests.fakes import FakeMockServiceClient, install_fake_fastmcp


class Ex05BuildToolTest(unittest.TestCase):
    def test_fetch_build_status(self):
        client = FakeMockServiceClient()
        result = fetch_build_status("BLD-203", client=client)
        self.assertTrue(result["ok"])
        self.assertEqual(result["id"], "BLD-203")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failed_step"], "integration-tests")
        self.assertIn("log_excerpt", result)
        self.assertEqual(client.build_ids, ["BLD-203"])

    def test_fetch_build_missing(self):
        result = fetch_build_status("BLD-999", client=FakeMockServiceClient())
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_fastmcp_server_registers_and_executes_build_tool(self):
        install_fake_fastmcp()
        sys.modules.pop("stack_sentinel.mcp_server.fastmcp_server", None)
        fastmcp_server = importlib.import_module("stack_sentinel.mcp_server.fastmcp_server")

        original_client = tool_module.MockServiceClient
        tool_module.MockServiceClient = FakeMockServiceClient
        try:
            server = fastmcp_server.create_fastmcp_server()
            self.assertEqual(server.name, "stack-sentinel-mcp")
            self.assertIn(BUILD_TOOL_NAME, server.tools)

            result = server.tools[BUILD_TOOL_NAME]("BLD-203")
            self.assertTrue(result["ok"])
            self.assertEqual(result["id"], "BLD-203")
            self.assertEqual(result["failed_step"], "integration-tests")
        finally:
            tool_module.MockServiceClient = original_client


if __name__ == "__main__":
    unittest.main()
