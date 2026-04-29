import unittest

from stack_sentinel.agent.graph import compile_minimal_graph


class Ex08GraphMinimalTest(unittest.TestCase):
    def test_minimal_langgraph_invokes(self):
        graph = compile_minimal_graph()
        self.assertTrue(callable(getattr(graph, "invoke", None)))

        result = graph.invoke({"user_input": "ping"})
        self.assertEqual(result["final_answer"], "ping")
        self.assertEqual(result["user_input"], "ping")

    def test_minimal_graph_has_echo_node(self):
        graph = compile_minimal_graph()
        graph_repr = graph.get_graph()
        node_names = {node.name for node in graph_repr.nodes.values()}
        self.assertIn("echo", node_names)


if __name__ == "__main__":
    unittest.main()
