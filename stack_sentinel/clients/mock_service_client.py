import json
import os
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_BASE_URL = os.getenv("STACK_SENTINEL_BASE_URL", "http://127.0.0.1:8000")

MOCK_ENDPOINTS = {
    "health": "/health",
    "tickets": "/tickets/{ticket_id}",
    "builds": "/builds/{build_id}",
    "docs": "/docs/{slug}",
    "service_health": "/services/{service_name}/health",
    "incidents": "/incidents/{incident_id}",
}


class MockServiceClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_json(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"ok": False, "error": f"http {exc.code}"}
        except URLError as exc:
            return {"ok": False, "error": f"mock service unavailable: {exc.reason}"}

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return self.get_json(MOCK_ENDPOINTS["tickets"].format(ticket_id=ticket_id))

    def get_build(self, build_id: str) -> Dict[str, Any]:
        return self.get_json(MOCK_ENDPOINTS["builds"].format(build_id=build_id))

    def get_doc(self, slug: str) -> Dict[str, Any]:
        return self.get_json(MOCK_ENDPOINTS["docs"].format(slug=slug))

    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        return self.get_json(MOCK_ENDPOINTS["service_health"].format(service_name=service_name))


def check_mock_service_health(client: Optional[MockServiceClient] = None) -> bool:
    """Contrato do Ex01: retorna True se o health check da mock API estiver OK."""
    client = client or MockServiceClient()
    try:
        response = client.get_json(MOCK_ENDPOINTS["health"])
    except Exception:
        return False
    return response.get("ok") is True
