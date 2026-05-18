import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()


# ---------------------------
# LLM Setup
# ---------------------------

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.3-70b-versatile"
)


# ---------------------------
# State
# ---------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# ---------------------------
# Tool
# ---------------------------

@tool
def fake_search(query: str) -> str:
    """
    Search the web for information related to the given query.
    Returns a fake hardcoded search result.
    """
    return f"Fake search result for '{query}': LangGraph is awesome for building AI agents!"


tools = [fake_search]


# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)


# ---------------------------
# Agent Node
# ---------------------------

def agent_node(state: State):

    response = llm_with_tools.invoke(state["messages"]) # here tbe llm will read the message and may add tool calls in the AIMessage or it will return a normal AIMessage without tool calls. 

    return {
        "messages": [response] # add the AIMessage in the messages
    }


# ---------------------------
# Tool Node
# ---------------------------

tool_node = ToolNode(tools) # here we create the tool node


# ---------------------------
# Conditional Routing
# ---------------------------

def should_continue(state: State):

    last_message = state["messages"][-1]

    # If the LLM requested tool calls
    if last_message.tool_calls:
        return "tools"

    # Otherwise stop
    return "end"


# ---------------------------
# Graph Setup
# ---------------------------

graph_builder = StateGraph(State)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent") # start the graph with the agent node, which processes the initial messages and may make tool calls

graph_builder.add_conditional_edges(
    "agent", #frist agent proceses the message and comes back with tool calls aargument
    should_continue, # heree it reads if the last message had any tool calls, if yes it goes to tools node, if not it goes to end
    {
        "tools": "tools", # here the tool node processes the tool calls and comes back with the tool results in the messages (ToolMessage addded)
        "end": END # if there are no tool calls, we end the graph execution and return the messages as they are
    }
)

graph_builder.add_edge("tools", "agent") # after the tool node processes the tool calls, we go back to the agent node with the updated messages (which now include the tool results). The agent can then decide to make more tool calls or end the execution based on the new messages.

graph = graph_builder.compile()


# ---------------------------
# Run Graph
# ---------------------------

result = graph.invoke({
    "messages": [
        HumanMessage(content="Search LangGraph")
    ]
})


# ---------------------------
# Print Final Messages
# ---------------------------

for message in result["messages"]:
    print(message)



