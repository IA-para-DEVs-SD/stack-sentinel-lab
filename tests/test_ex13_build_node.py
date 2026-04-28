import unittest

from stack_sentinel.agent.nodes import fetch_build_node
from tests.fakes import fastmcp_test_client


class Ex13BuildNodeTest(unittest.TestCase):
    def test_fetch_build_node_updates_context(self):
        state = {"user_input": "O build BLD-203 esta quebrado?", "build_id": None}
        with fastmcp_test_client() as client:
            result = fetch_build_node(state, client)
        self.assertEqual(result["build_id"], "BLD-203")
        self.assertEqual(result["context"]["id"], "BLD-203")
        self.assertEqual(result["context"]["status"], "failed")
        self.assertIsNone(result.get("error"))

    def test_fetch_build_node_uses_existing_build_id(self):
        with fastmcp_test_client() as client:
            result = fetch_build_node({"user_input": "sem id no texto", "build_id": "BLD-203"}, client)
        self.assertEqual(result["context"]["id"], "BLD-203")

    def test_fetch_build_node_handles_missing_build_id(self):
        with fastmcp_test_client() as client:
            result = fetch_build_node({"user_input": "sem build aqui"}, client)
        self.assertIn("error", result)
        self.assertIsNone(result.get("context"))


if __name__ == "__main__":
    unittest.main()
