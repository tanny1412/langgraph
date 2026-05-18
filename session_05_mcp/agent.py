import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage

from langgraph.prebuilt import ToolNode
from mcp.client.stdio import stdio_client # conects to a local mcp server and runs the server as a subprocess
from mcp import ClientSession, StdioServerParameters # client session to connect to the mcp server, and parameters is used to write which file has the mcp server code ie server.py
from langchain_mcp_adapters.tools import load_mcp_tools # translates mcp tool calls to langchain tool calls and vice versa because langgraph udnerstands langchain tools and not mcp tools directly


load_dotenv()

async def main():
    server_parameters = StdioServerParameters(command="python3", args=["session_05_mcp/server.py"]) # specify which file has the mcp server code

    async with stdio_client(server_parameters) as (read,write): # point where is the mcp server code located/running , read for client to read(outputs from tools) from mcp server, write for client to write(requests) to mcp server
        async with ClientSession(read, write) as session: # establish a connection with the mcp server (wraps the stdio transport layer(above line) around the mcp server - so now it is can speak real mcp protocol language over stdio)
            await session.initialize() # initialize the mcp session, handshakes happens here, now we can send tool calls to the mcp server and get responses back from it
            tools = await load_mcp_tools(session) # load the tools from the mcp server and translate them to langchain tool format so that langgraph can understand and use them in the agent node
            print("Tools loaded from MCP server:", tools)


            llm = ChatOpenAI(
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.1-8b-instant"
            )

            llm_with_tools = llm.bind_tools(tools)

            class State(TypedDict):
                messages: Annotated[list, add_messages]


            async def agent_node(state: State):

                response = await llm_with_tools.ainvoke(
                    state["messages"]
                )

                return {
                    "messages": [response]
                }
            
            tool_node = ToolNode(tools)


            def should_continue(state: State):

                last_message = state["messages"][-1]

                if last_message.tool_calls:
                    return "tools"

                return "end"
            
            graph = StateGraph(State)
            graph.add_node("agent", agent_node)
            graph.add_node("tools", tool_node)

            graph.add_edge(START, "agent") # start the graph with the agent node, which processes the initial messages and may make tool calls
            graph.add_conditional_edges(
                "agent", #frist agent proceses the message and comes back with tool calls aargument
                should_continue, # heree it reads if the last message had any tool calls, if yes it goes to tools node, if not it goes to end
                {
                    "tools": "tools", # here the tool node processes the tool calls and comes back with the tool results in the messages (ToolMessage addded)
                    "end": END # if there are no tool calls, we end the graph execution and return the messages as they are
                }
             )
            graph.add_edge("tools", "agent") # after the tool node processes the tool calls, we go back to the agent node with the updated messages (which now include the tool results). The agent can then decide to make more tool calls or end the execution based on the new messages. 
            
            app = graph.compile()
            print("Invoking graph...")
            result = await app.ainvoke({"messages": [HumanMessage(content="What is the meaning of life?")]})
    
            print("Result:",result)

asyncio.run(main())









        





            










    
