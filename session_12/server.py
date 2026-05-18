import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP("search-server")
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for current information on any topic. Use concise, keyword-focused queries."""
    results = tavily.search(query=query, max_results=3)
    output = []
    for r in results["results"]:
        output.append(f"Source: {r['url']}\n{r['content']}")
    return "\n\n".join(output)


if __name__ == "__main__":
    mcp.run(transport="stdio")
