from stack_sentinel.mcp_server import prompts, resources, tools
from stack_sentinel.shared.contracts import INCIDENT_RESPONSE_RESOURCE

def create_fastmcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("stack-sentinel-mcp")

    @mcp.tool()
    def fetch_ticket_context(ticket_id: str) -> dict:
        """Busca contexto normalizado de um ticket."""
        return tools.fetch_ticket_context(ticket_id)

    @mcp.tool()
    def fetch_build_status(build_id: str) -> dict:
        """Busca status e evidencias de um build."""
        return tools.fetch_build_status(build_id)

    @mcp.resource(INCIDENT_RESPONSE_RESOURCE)
    def incident_response_resource() -> dict:
        return resources.read_doc_resource(INCIDENT_RESPONSE_RESOURCE)

    @mcp.prompt()
    def incident_triage_prompt(user_question: str, available_context: str) -> str:
        return prompts.incident_triage_prompt(user_question, available_context)

    return mcp


def run_fastmcp_server() -> None:
    create_fastmcp_server().run()


if __name__ == "__main__":
    run_fastmcp_server()
