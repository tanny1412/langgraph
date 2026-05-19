import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP("billing-tools-server")
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


@mcp.tool()
def web_search(query: str) -> str:
    """Search for billing policies, refund procedures, and payment information."""
    results = tavily.search(query=query, max_results=3)
    output = []
    for r in results["results"]:
        output.append(f"Source: {r['url']}\n{r['content']}")
    return "\n\n".join(output)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8081
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["*", "billing-mcp-server:8081"],
    )
    mcp.run(transport="streamable-http")
