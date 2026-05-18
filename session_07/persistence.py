import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.1-8b-instant"
)


class State(TypedDict):
    messages: Annotated[list, add_messages]

# -----------------------------------
# Supervisor Agent
# -----------------------------------

def agent_node(state: State):
    
    response = llm.invoke(
    state["messages"]
    )

    return {
    "messages": [response]
    }

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_edge(START, "agent") # start the graph with the agent node, which
# processes the initial messages and may make tool calls

graph.add_edge("agent", END) # after the agent processes the messages, we end
# the graph execution and return the agent's response
with SqliteSaver.from_conn_string("session_07/conversations.db") as checkpointer:
    graph_app = graph.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "user-1"}}


    result = graph_app.invoke({"messages": [HumanMessage(content="My name is Tanish")]}, config=config)
    result = graph_app.invoke({"messages": [HumanMessage(content="What is my name?")]}, config=config)
    print(result["messages"][-1].content)
