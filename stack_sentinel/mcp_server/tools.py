from typing import Any, Dict, Optional

from stack_sentinel.clients.mock_service_client import MockServiceClient


def fetch_ticket_context(ticket_id: str, client: Optional[MockServiceClient] = None) -> Dict[str, Any]:
    """Contrato do Ex02: retorna contexto normalizado de um ticket."""
    if not ticket_id:
        return {"ok": False, "error": "ticket_id is required"}

    client = client or MockServiceClient()
    response = client.get_ticket(ticket_id)

    if not response.get("ok"):
        return {"ok": False, "error": response.get("error", "ticket not found")}

    data = response.get("data") or {}
    return {
        "ok": True,
        "id": data.get("id"),
        "summary": data.get("summary"),
        "severity": data.get("severity"),
        "service": data.get("service"),
        "status": data.get("status"),
        "build_id": data.get("build_id"),
    }


def fetch_build_status(build_id: str, client: Optional[MockServiceClient] = None) -> Dict[str, Any]:
    """Contrato do Ex05: retorna status normalizado de um build."""
    if not build_id:
        return {"ok": False, "error": "build_id is required"}

    client = client or MockServiceClient()
    response = client.get_build(build_id)

    if not response.get("ok"):
        return {"ok": False, "error": response.get("error", "build not found")}

    data = response.get("data") or {}
    return {
        "ok": True,
        "id": data.get("id"),
        "status": data.get("status"),
        "service": data.get("service"),
        "branch": data.get("branch"),
        "failed_step": data.get("failed_step"),
        "log_excerpt": data.get("log_excerpt"),
    }
