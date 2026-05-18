from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    question: str
    answer: str

def router(state: State) -> str:
    if "database" in state["question"].lower():
        return "database"
    else:
        return "simple"
    
def answer_simple(state: State) -> dict:
    return {"answer": "I answered from my knowledge base!"}

def answer_database(state: State) -> dict:
    return {"answer": "I answered from the database!"}

graph = StateGraph(State)

graph.add_node("database", answer_database)
graph.add_node("simple", answer_simple)

graph.add_conditional_edges(START,
                           router)


graph.add_edge("simple", END)
graph.add_edge("database", END)

app = graph.compile()

result = app.invoke({"question": "What is the capital of France?"})
print(result)