import importlib
import sys
import unittest

from stack_sentinel.mcp_server import resources as resources_module
from stack_sentinel.mcp_server.resources import list_doc_resources, read_doc_resource
from stack_sentinel.shared.contracts import INCIDENT_RESPONSE_RESOURCE, SEVERITY_POLICY_RESOURCE
from tests.fakes import FakeMockServiceClient, install_fake_fastmcp


class Ex06ResourcesTest(unittest.TestCase):
    def test_list_resources_contains_required_uris(self):
        uris = {item["uri"] for item in list_doc_resources()}
        self.assertIn(INCIDENT_RESPONSE_RESOURCE, uris)
        self.assertIn(SEVERITY_POLICY_RESOURCE, uris)

    def test_read_resource(self):
        client = FakeMockServiceClient()
        result = read_doc_resource(INCIDENT_RESPONSE_RESOURCE, client=client)
        self.assertTrue(result["ok"])
        self.assertEqual(result["uri"], INCIDENT_RESPONSE_RESOURCE)
        self.assertIn("Incident Response", result["title"])
        self.assertIn("severidade", result["content"])
        self.assertEqual(client.doc_slugs, ["incident-response"])

    def test_read_unknown_resource_returns_controlled_error(self):
        result = read_doc_resource("docs://missing", client=FakeMockServiceClient())
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_fastmcp_server_registers_and_executes_incident_response_resource(self):
        install_fake_fastmcp()
        sys.modules.pop("stack_sentinel.mcp_server.fastmcp_server", None)
        fastmcp_server = importlib.import_module("stack_sentinel.mcp_server.fastmcp_server")

        original_client = resources_module.MockServiceClient
        resources_module.MockServiceClient = FakeMockServiceClient
        try:
            server = fastmcp_server.create_fastmcp_server()
            self.assertEqual(server.name, "stack-sentinel-mcp")
            self.assertIn(INCIDENT_RESPONSE_RESOURCE, server.resources)

            result = server.resources[INCIDENT_RESPONSE_RESOURCE]()
            self.assertTrue(result["ok"])
            self.assertEqual(result["uri"], INCIDENT_RESPONSE_RESOURCE)
            self.assertIn("Incident Response", result["title"])
        finally:
            resources_module.MockServiceClient = original_client


if __name__ == "__main__":
    unittest.main()
