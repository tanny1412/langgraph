import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.1-8b-instant"
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State):
    full_response = None
    for token in llm.stream(state["messages"]):
#       print(token.content, end="", flush=True)  # print the token
        if full_response is None:
            full_response = token
        else:
            full_response = full_response + token

    return {"messages": [full_response]}


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)

graph = graph.compile()

for event in graph.stream(
    {"messages": [HumanMessage(content="Tell me a fun fact about space")]},
    stream_mode="updates"
):
    print(event) # this will change to yield in the backend code POST/chat endpoint
