import importlib
import sys
import unittest

from stack_sentinel.mcp_server.prompts import incident_triage_prompt
from stack_sentinel.shared.contracts import INCIDENT_TRIAGE_PROMPT
from tests.fakes import install_fake_fastmcp


class Ex07PromptsTest(unittest.TestCase):
    def test_incident_triage_prompt_contains_required_instructions(self):
        prompt = incident_triage_prompt(
            user_question="Como tratar incidente critico?",
            available_context="critical: impacto financeiro relevante",
        )
        lower = prompt.lower()
        self.assertIn("resum", lower)
        self.assertIn("severidade", lower)
        self.assertIn("proximo passo", lower)
        self.assertIn("nao invent", lower)
        self.assertIn("como tratar incidente critico", lower)
        self.assertIn("critical", lower)

    def test_fastmcp_server_registers_and_executes_incident_triage_prompt(self):
        install_fake_fastmcp()
        sys.modules.pop("stack_sentinel.mcp_server.fastmcp_server", None)
        fastmcp_server = importlib.import_module("stack_sentinel.mcp_server.fastmcp_server")

        server = fastmcp_server.create_fastmcp_server()
        self.assertIn(INCIDENT_TRIAGE_PROMPT, server.prompts)

        result = server.get_prompt(
            INCIDENT_TRIAGE_PROMPT,
            {
                "user_question": "Como tratar incidente critico?",
                "available_context": "critical: impacto financeiro relevante",
            },
        )
        self.assertTrue(result["ok"])
        self.assertIn("nao invent", result["content"].lower())


if __name__ == "__main__":
    unittest.main()
