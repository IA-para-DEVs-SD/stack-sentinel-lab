class LLMClient:
    def classify_intent(self, user_input: str) -> str:
        raise NotImplementedError

    def extract_ticket_id(self, user_input: str):
        return None
