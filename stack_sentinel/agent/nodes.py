from stack_sentinel.agent.state import AgentState, update_state
from stack_sentinel.clients.mcp_client import MCPClient
from stack_sentinel.llm.base import LLMClient
from stack_sentinel.shared.contracts import (
    BUILD_TOOL_NAME,
    INCIDENT_RESPONSE_RESOURCE,
    INCIDENT_TRIAGE_PROMPT,
    TICKET_TOOL_NAME,
)
from stack_sentinel.shared.utils import extract_build_id, extract_ticket_id


def classify_intent_node(state: AgentState, llm: LLMClient) -> AgentState:
    """Contrato do Ex10: classifica a intencao e atualiza state['intent']."""
    user_input = state.get("user_input", "")
    intent = llm.classify_intent(user_input)
    if intent not in {"ticket", "build", "docs", "unknown"}:
        intent = "unknown"

    ticket_id = None
    if hasattr(llm, "extract_ticket_id"):
        ticket_id = llm.extract_ticket_id(user_input)
    ticket_id = ticket_id or extract_ticket_id(user_input)

    changes = {"intent": intent}
    if ticket_id:
        changes["ticket_id"] = ticket_id
    return update_state(state, **changes)


def fetch_ticket_node(state: AgentState, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex12: consulta a tool MCP de ticket e atualiza o state."""
    ticket_id = state.get("ticket_id") or extract_ticket_id(state.get("user_input", ""))
    if not ticket_id:
        return update_state(state, ticket_id=None, context=None, error="ticket_id not found")

    result = mcp_client.call_tool(TICKET_TOOL_NAME, {"ticket_id": ticket_id})
    if not result.get("ok"):
        return update_state(
            state,
            ticket_id=ticket_id,
            context=None,
            error=result.get("error", "ticket tool failed"),
        )

    return update_state(state, ticket_id=ticket_id, context=result, error=None)


def fetch_build_node(state: AgentState, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex13: consulta a tool MCP de build e atualiza o state."""
    build_id = state.get("build_id") or extract_build_id(state.get("user_input", ""))
    if not build_id:
        return update_state(state, build_id=None, context=None, error="build_id not found")

    result = mcp_client.call_tool(BUILD_TOOL_NAME, {"build_id": build_id})
    if not result.get("ok"):
        return update_state(
            state,
            build_id=build_id,
            context=None,
            error=result.get("error", "build tool failed"),
        )

    return update_state(state, build_id=build_id, context=result, error=None)


def fetch_docs_node(state: AgentState, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex14: le resource/prompt MCP e atualiza o context."""
    resource = mcp_client.read_resource(INCIDENT_RESPONSE_RESOURCE)
    if not resource.get("ok"):
        return update_state(state, context=None, error=resource.get("error", "resource read failed"))

    prompt = mcp_client.get_prompt(
        INCIDENT_TRIAGE_PROMPT,
        {
            "user_question": state.get("user_input", ""),
            "available_context": resource.get("content", ""),
        },
    )
    if not prompt.get("ok"):
        return update_state(state, context=None, error=prompt.get("error", "prompt read failed"))

    return update_state(state, context={"resource": resource, "prompt": prompt}, error=None)


def fallback_node(state: AgentState) -> AgentState:
    return update_state(
        state,
        error="Nao encontrei uma rota segura para esta pergunta.",
        final_answer="Nao consegui identificar se a pergunta e sobre ticket, build ou documentacao.",
    )


def _value_or_missing(value) -> str:
    if value is None or value == "":
        return "nao informado"
    return str(value)


def _ticket_answer_prompt(context: dict) -> str:
    return (
        "Transforme o JSON normalizado de ticket em uma resposta operacional curta.\n"
        "Use exatamente as secoes: Resumo, Evidencias e Proximo passo.\n"
        "Decomponha os campos assim:\n"
        f"- id: {_value_or_missing(context.get('id'))}\n"
        f"- summary: {_value_or_missing(context.get('summary'))}\n"
        f"- severity: {_value_or_missing(context.get('severity'))}\n"
        f"- service: {_value_or_missing(context.get('service'))}\n"
        f"- status: {_value_or_missing(context.get('status'))}\n"
        f"- build_id: {_value_or_missing(context.get('build_id'))}\n"
        "Nao invente campos ausentes."
    )


def final_answer_node(state: AgentState) -> AgentState:
    """Contrato do Ex15: transforma state/context em resposta final."""
    intent = state.get("intent")
    context = state.get("context") or {}

    if state.get("final_answer"):
        return state

    if state.get("error") and not context:
        return update_state(state, final_answer=f"Nao consegui responder com seguranca: {state['error']}")

    if intent == "ticket":
        response_prompt = _ticket_answer_prompt(context)
        answer = (
            f"Resumo: ticket {_value_or_missing(context.get('id'))} - "
            f"{_value_or_missing(context.get('summary'))}\n"
            "Evidencias: "
            f"severidade {_value_or_missing(context.get('severity'))}; "
            f"servico {_value_or_missing(context.get('service'))}; "
            f"status {_value_or_missing(context.get('status'))}; "
            f"build relacionado {_value_or_missing(context.get('build_id'))}.\n"
            "Proximo passo: verificar o build relacionado, validar o healthcheck do servico "
            "e atualizar o ticket com a evidencia encontrada."
        )
        return update_state(state, final_answer=answer, response_prompt=response_prompt)

    if intent == "build":
        answer = (
            f"Resumo: build {_value_or_missing(context.get('id'))} esta com status "
            f"{_value_or_missing(context.get('status'))}.\n"
            "Evidencias: "
            f"servico {_value_or_missing(context.get('service'))}; "
            f"branch {_value_or_missing(context.get('branch'))}; "
            f"etapa falha {_value_or_missing(context.get('failed_step'))}; "
            f"log {_value_or_missing(context.get('log_excerpt'))}.\n"
            "Proximo passo: revisar a etapa falha e correlacionar com tickets recentes."
        )
        return update_state(state, final_answer=answer)

    if intent == "docs":
        resource = context.get("resource", {})
        prompt = context.get("prompt", {})
        answer = (
            f"Resumo: consulte {_value_or_missing(resource.get('title'))} para orientar a triagem.\n"
            f"Evidencias: {_value_or_missing(resource.get('content'))}\n"
            f"Proximo passo: {_value_or_missing(prompt.get('content'))}"
        )
        return update_state(state, final_answer=answer)

    return update_state(
        state,
        final_answer="Nao consegui identificar se a pergunta e sobre ticket, build ou documentacao.",
    )
