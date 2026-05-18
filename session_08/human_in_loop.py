import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
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


def agent_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)

with SqliteSaver.from_conn_string("session_08/conversations.db") as checkpointer:
    graph_app = graph.compile(checkpointer=checkpointer, interrupt_after=["agent"])

    config = {"configurable": {"thread_id": "user-1"}}

    result = graph_app.invoke({"messages": [HumanMessage(content="My name is Tanish")]}, config=config)
    human_input = input("Agent paused. Press Enter to continue, or type a new message: ")
    result = graph_app.invoke(None, config=config)  

    result = graph_app.invoke({"messages": [HumanMessage(content="What is my name?")]}, config=config)
    human_input = input("Agent paused. Press Enter to continue: ")
    result = graph_app.invoke(None, config=config)
    print(result["messages"][-1].content)
