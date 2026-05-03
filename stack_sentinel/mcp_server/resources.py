from typing import Any, Dict, Optional

from stack_sentinel.clients.mock_service_client import MockServiceClient
from stack_sentinel.shared.contracts import (
    BUILD_FAILURE_PLAYBOOK_RESOURCE,
    INCIDENT_RESPONSE_RESOURCE,
    SERVICE_CATALOG_RESOURCE,
    SEVERITY_POLICY_RESOURCE,
)


RESOURCE_TO_SLUG = {
    INCIDENT_RESPONSE_RESOURCE: "incident-response",
    SEVERITY_POLICY_RESOURCE: "severity-policy",
    SERVICE_CATALOG_RESOURCE: "service-catalog",
    BUILD_FAILURE_PLAYBOOK_RESOURCE: "build-failure-playbook",
}


def read_doc_resource(uri: str, client: Optional[MockServiceClient] = None) -> Dict[str, Any]:
    """Contrato do Ex06: retorna conteudo de um resource docs://..."""
    if uri not in RESOURCE_TO_SLUG:
        return {"ok": False, "error": f"unknown resource: {uri}"}

    client = client or MockServiceClient()
    slug = RESOURCE_TO_SLUG[uri]
    response = client.get_doc(slug)

    if not response.get("ok"):
        return {"ok": False, "error": response.get("error", "resource not found")}

    data = response.get("data") or {}
    return {
        "ok": True,
        "uri": uri,
        "title": data.get("title"),
        "content": data.get("content"),
    }


def list_doc_resources() -> list[dict]:
    return [
        {
            "uri": INCIDENT_RESPONSE_RESOURCE,
            "name": "Incident Response Guide",
            "description": "Runbook para triagem e resposta a incidentes.",
        },
        {
            "uri": SEVERITY_POLICY_RESOURCE,
            "name": "Severity Policy",
            "description": "Politica de classificacao de severidade.",
        },
        {
            "uri": SERVICE_CATALOG_RESOURCE,
            "name": "Service Catalog",
            "description": "Catalogo de servicos, donos e criticidade.",
        },
        {
            "uri": BUILD_FAILURE_PLAYBOOK_RESOURCE,
            "name": "Build Failure Playbook",
            "description": "Guia rapido para investigar builds quebrados.",
        },
    ]
