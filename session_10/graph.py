from langgraph.graph import StateGraph, START, END
from session_10.state import State
from session_10.agents import agent_node

graph_builder = StateGraph(State)
graph_builder.add_node("agent", agent_node)
graph_builder.add_edge(START, "agent")
graph_builder.add_edge("agent", END)
