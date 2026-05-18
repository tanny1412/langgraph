from mcp.server.fastmcp import FastMCP

mcp = FastMCP("search-server")


@mcp.tool()
def fake_search(query: str) -> str:
    """
    Search for information on a topic. Use concise, keyword-focused queries.
    Returns relevant search results.
    """
    return f"Search result for '{query}': LangGraph is a graph-based framework for building stateful AI agents."


if __name__ == "__main__":
    mcp.run(transport="stdio") # for local server, runs as a subprocess in the client code. but for hosted servers, use transport="sse"


