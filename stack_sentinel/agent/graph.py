from typing import Any

from langgraph.graph import END, START, StateGraph

from stack_sentinel.agent.state import AgentState
from stack_sentinel.clients.mcp_client import MCPClient
from stack_sentinel.llm.base import LLMClient


def compile_minimal_graph() -> Any:
    """Contrato do Ex08: cria um grafo LangGraph minimo executavel."""

    def echo_node(state: AgentState) -> AgentState:
        return {
            "user_input": state.get("user_input"),
            "final_answer": state.get("user_input"),
        }

    graph = StateGraph(AgentState)
    graph.add_node("echo", echo_node)
    graph.add_edge(START, "echo")
    graph.add_edge("echo", END)
    return graph.compile()


def route_by_intent(state: AgentState) -> str:
    routes = {
        "ticket": "fetch_ticket",
        "build": "fetch_build",
        "docs": "fetch_docs",
    }
    return routes.get(state.get("intent"), "fallback")


def run_stack_sentinel_flow(state: AgentState, llm: LLMClient, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex16: executa o fluxo final ponta a ponta."""
    from stack_sentinel.agent.nodes import (
        classify_intent_node,
        fallback_node,
        fetch_build_node,
        fetch_docs_node,
        fetch_ticket_node,
        final_answer_node,
    )

    current = classify_intent_node(state, llm)
    route = route_by_intent(current)

    if route == "fetch_ticket":
        current = fetch_ticket_node(current, mcp_client)
    elif route == "fetch_build":
        current = fetch_build_node(current, mcp_client)
    elif route == "fetch_docs":
        current = fetch_docs_node(current, mcp_client)
    else:
        current = fallback_node(current)

    return final_answer_node(current)
