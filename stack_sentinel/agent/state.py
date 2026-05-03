from typing import Any, Dict, Optional, TypedDict


class AgentState(TypedDict, total=False):
    user_input: str
    intent: Optional[str]
    ticket_id: Optional[str]
    build_id: Optional[str]
    context: Optional[Dict[str, Any]]
    error: Optional[str]
    final_answer: Optional[str]


def create_initial_state(user_input: str) -> AgentState:
    return {
        "user_input": user_input,
        "intent": None,
        "ticket_id": None,
        "build_id": None,
        "context": None,
        "error": None,
        "final_answer": None,
    }


def update_state(state: AgentState, **changes: Any) -> AgentState:
    updated = dict(state)
    updated.update(changes)
    return updated  # type: ignore[return-value]
