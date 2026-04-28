import unittest

from stack_sentinel.agent.nodes import fetch_docs_node
from tests.fakes import fastmcp_test_client


class Ex14ResourcesPromptsNodeTest(unittest.TestCase):
    def test_fetch_docs_node_updates_context_with_resource_and_prompt(self):
        state = {"user_input": "Como devo tratar incidente critico?"}
        with fastmcp_test_client() as client:
            result = fetch_docs_node(state, client)
        self.assertTrue(result["context"]["resource"]["ok"])
        self.assertTrue(result["context"]["prompt"]["ok"])
        self.assertIn("Incident Response", result["context"]["resource"]["title"])
        self.assertIn("nao invente", result["context"]["prompt"]["content"])
        self.assertIsNone(result.get("error"))
        self.assertIn("resource", result["context"])
        self.assertIn("prompt", result["context"])


if __name__ == "__main__":
    unittest.main()
