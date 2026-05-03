def incident_triage_prompt(user_question: str, available_context: str) -> str:
    """Contrato do Ex07: retorna um prompt de triagem de incidente."""
    return (
        "Voce e um agente de triagem de incidentes. "
        f"Pergunta do usuario: {user_question}. "
        f"Contexto disponivel: {available_context}. "
        "Resuma o problema, cite severidade quando houver evidencia, "
        "sugira proximo passo e nao invente dados ausentes."
    )
