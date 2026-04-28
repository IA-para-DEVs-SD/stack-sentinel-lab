from stack_sentinel.mcp_server import tools


def create_fastmcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("stack-sentinel-mcp")

    @mcp.tool()
    def fetch_ticket_context(ticket_id: str) -> dict:
        """Busca contexto normalizado de um ticket."""
        return tools.fetch_ticket_context(ticket_id)

    return mcp


def run_fastmcp_server() -> None:
    create_fastmcp_server().run()


if __name__ == "__main__":
    run_fastmcp_server()
