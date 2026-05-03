import os
import json
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from stack_sentinel.llm.base import LLMClient
from stack_sentinel.shared.utils import extract_ticket_id


class ProviderLLMClient(LLMClient):
    """Cliente opcional para usar uma LLM real fora dos testes obrigatorios.

    O lab nao depende deste cliente para passar nos exercicios. Ele existe para
    demos ou alunos que ja tenham chave configurada e queiram comparar uma LLM
    real com o FakeLLM.
    """

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")

    def classify_intent(self, user_input: str) -> str:
        """Classifica intencao usando Gemini quando configurado.

        O contrato continua simples: retornar apenas ticket, build, docs ou
        unknown. Os testes obrigatorios seguem usando FakeLLMClient.
        """
        prompt = (
            "Classifique a intencao da pergunta do usuario. "
            "Responda somente com uma destas palavras: ticket, build, docs, unknown.\n\n"
            f"Pergunta: {user_input}"
        )
        return self.normalize_intent(self._generate_text(prompt))

    def extract_ticket_id(self, user_input: str):
        deterministic = extract_ticket_id(user_input)
        if deterministic:
            return deterministic

        prompt = (
            "Extraia o ID de ticket da mensagem do usuario. "
            "O formato valido e TCK-000, com qualquer quantidade de digitos. "
            "Se nao houver ID de ticket, responda somente NONE.\n\n"
            f"Mensagem: {user_input}"
        )
        value = self._generate_text(prompt).strip().upper()
        return None if value == "NONE" else extract_ticket_id(value)

    def _generate_text(self, prompt: str) -> str:
        if self.provider != "gemini":
            raise RuntimeError(f"Provider nao suportado: {self.provider}")
        if not self.api_key:
            raise RuntimeError(
                "Gemini nao configurado. Defina GEMINI_API_KEY ou LLM_API_KEY."
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ]
        }
        request = Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            raise RuntimeError(f"Gemini HTTP error {exc.code}: {body}") from exc
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc

        candidates = payload.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts") or []
        return "".join(part.get("text", "") for part in parts).strip()

    @staticmethod
    def normalize_intent(value: str) -> str:
        allowed = {"ticket", "build", "docs", "unknown"}
        normalized = value.strip().lower()
        return normalized if normalized in allowed else "unknown"
