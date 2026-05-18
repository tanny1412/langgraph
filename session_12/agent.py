import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated, TypedDict
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()


async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["session_12/server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print("Tools loaded:", [t.name for t in tools])

            llm = ChatOpenAI(
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
            llm_with_tools = llm.bind_tools(tools)

            class State(TypedDict):
                messages: Annotated[list, add_messages]

            async def agent_node(state: State):
                response = await llm_with_tools.ainvoke(state["messages"])
                return {"messages": [response]}

            def should_continue(state: State):
                if state["messages"][-1].tool_calls:
                    return "tools"
                return "end"

            graph = StateGraph(State)
            graph.add_node("agent", agent_node)
            graph.add_node("tools", ToolNode(tools))
            graph.add_edge(START, "agent")
            graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
            graph.add_edge("tools", "agent")

            app = graph.compile()

            result = await app.ainvoke(
                {"messages": [HumanMessage(content="Search for latest AI news today and summarize the top 3 results in bullet points.")]},
                {"recursion_limit": 5}
            )
            print("\nAnswer:", result["messages"][-1].content)


asyncio.run(main())
