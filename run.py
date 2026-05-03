import argparse
import importlib
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests"

TEST_MODULES = {
    "ex00": "tests.test_ex00_setup",
    "ex01": "tests.test_ex01_mock_service",
    "ex02": "tests.test_ex02_ticket_tool",
    "ex03": "tests.test_ex03_mcp_server",
    "ex04": "tests.test_ex04_mcp_ticket_tool",
    "ex05": "tests.test_ex05_build_tool",
    "ex06": "tests.test_ex06_resources",
    "ex07": "tests.test_ex07_prompts",
    "ex08": "tests.test_ex08_graph_minimal",
    "ex09": "tests.test_ex09_state",
    "ex10": "tests.test_ex10_classify_node",
    "ex11": "tests.test_ex11_routing",
    "ex12": "tests.test_ex12_ticket_node",
    "ex13": "tests.test_ex13_build_node",
    "ex14": "tests.test_ex14_resources_prompts_node",
    "ex15": "tests.test_ex15_final_answer",
    "ex16": "tests.test_ex16_integration",
}


def doctor() -> int:
    print(f"Python: {sys.version.split()[0]}")
    required_paths = [
        ROOT / "README.md",
        ROOT / "RULES.md",
        ROOT / "stack_sentinel",
        ROOT / "stack_sentinel" / "data" / "tickets.json",
        ROOT / "tests",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("Missing paths:")
        for item in missing:
            print(f" - {item}")
        return 1
    for module in [
        "stack_sentinel.mock_api.server",
        "stack_sentinel.mcp_server.registry",
        "stack_sentinel.agent.state",
        "stack_sentinel.llm.fake_client",
    ]:
        importlib.import_module(module)
    print("Doctor OK: estrutura e imports principais validos.")
    return 0


def setup() -> int:
    requirements = ROOT / "requirements.txt"
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)])
    return result.returncode


def run_tests(target: str) -> int:
    if target == "all":
        modules = list(TEST_MODULES.values())
    else:
        if target not in TEST_MODULES:
            print(f"Exercicio desconhecido: {target}")
            print("Use um destes:", ", ".join(TEST_MODULES))
            return 1
        modules = [TEST_MODULES[target]]

    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for module_name in modules:
        suite.addTests(loader.loadTestsFromName(module_name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def mock_api(port: int) -> int:
    from stack_sentinel.mock_api.server import run_server

    run_server(port=port)
    return 0


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def chat(use_fake_llm: bool) -> int:
    from stack_sentinel.agent.graph import run_stack_sentinel_flow
    from stack_sentinel.agent.state import create_initial_state
    from stack_sentinel.clients.mcp_client import create_fastmcp_client
    from stack_sentinel.llm.fake_client import FakeLLMClient
    from stack_sentinel.llm.provider_client import ProviderLLMClient

    load_dotenv(ROOT / ".env")

    llm = FakeLLMClient() if use_fake_llm else ProviderLLMClient()
    mcp_client = create_fastmcp_client()

    print("Stack Sentinel chat pronto. Digite 'sair' para encerrar.")
    print("Dica: deixe a Mock API rodando em outro terminal com `python run.py mock-api`.")

    while True:
        try:
            user_input = input("\nVoce> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            return 0

        if user_input.lower() in {"sair", "exit", "quit"}:
            print("Encerrando.")
            return 0
        if not user_input:
            continue

        state = create_initial_state(user_input)
        try:
            result = run_stack_sentinel_flow(state, llm=llm, mcp_client=mcp_client)
        except Exception as exc:
            print(f"Stack Sentinel> Nao consegui executar o agente: {exc}")
            continue

        print(f"Stack Sentinel> {result.get('final_answer')}")


def demo() -> int:
    from stack_sentinel.agent.graph import run_stack_sentinel_flow
    from stack_sentinel.agent.state import create_initial_state
    from stack_sentinel.clients.mcp_client import MCPClient
    from stack_sentinel.llm.fake_client import FakeLLMClient
    from stack_sentinel.mcp_server.server import create_configured_mcp_server

    server = create_configured_mcp_server()
    client = MCPClient(server)
    llm = FakeLLMClient()
    questions = [
        "Qual o status do ticket TCK-101?",
        "O build BLD-203 esta quebrado?",
        "Como devo tratar incidente critico?",
        "Qual a capital da Franca?",
    ]
    for question in questions:
        state = create_initial_state(question)
        result = run_stack_sentinel_flow(state, llm=llm, mcp_client=client)
        print("\nPergunta:", question)
        print(result.get("final_answer"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("setup")
    api_parser = sub.add_parser("mock-api")
    api_parser.add_argument("--port", type=int, default=8000)
    test_parser = sub.add_parser("test")
    test_parser.add_argument("target")
    sub.add_parser("demo")
    chat_parser = sub.add_parser("chat")
    chat_parser.add_argument("--fake-llm", action="store_true", help="Usa FakeLLMClient em vez do Gemini.")
    args = parser.parse_args()

    os.chdir(ROOT)
    if args.command == "doctor":
        return doctor()
    if args.command == "setup":
        return setup()
    if args.command == "mock-api":
        return mock_api(args.port)
    if args.command == "test":
        return run_tests(args.target)
    if args.command == "demo":
        return demo()
    if args.command == "chat":
        return chat(use_fake_llm=args.fake_llm)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
