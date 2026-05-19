import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP("technical-tools-server")
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


@mcp.tool()
def web_search(query: str) -> str:
    """Search for technical documentation, error solutions, and API references."""
    results = tavily.search(query=query, max_results=3)
    output = []
    for r in results["results"]:
        output.append(f"Source: {r['url']}\n{r['content']}")
    return "\n\n".join(output)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8082
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["*", "technical-mcp-server:8082"],
    )
    mcp.run(transport="streamable-http")
