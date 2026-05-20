import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings
from tavily import TavilyClient
from final_project.rag.knowledge_base import build_knowledge_base, search_docs

load_dotenv()

mcp = FastMCP("billing-tools-server")
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
vectorstore = build_knowledge_base()


@mcp.tool()
def web_search(query: str) -> str:
    """Search the internet for billing policies, refund procedures, and payment information."""
    results = tavily.search(query=query, max_results=3)
    output = []
    for r in results["results"]:
        output.append(f"Source: {r['url']}\n{r['content']}")
    return "\n\n".join(output)


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Search internal company documents for refund policies, subscription terms, billing disputes, and payment methods."""
    return search_docs(query, vectorstore)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8081
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["*", "billing-mcp-server:8081"],
    )
    mcp.run(transport="streamable-http")
