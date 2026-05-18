from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str
    word_count: int


def count_words(state: State) -> dict:
    words = state["message"].split()
    return {"word_count": len(words)}

def make_uppercase(state: State) -> dict:
    uppercase_message = state["message"].upper()
    return {"message": uppercase_message}


graph = StateGraph(State)
graph.add_node("count_words", count_words)
graph.add_node("make_uppercase", make_uppercase)
graph.add_edge(START, "count_words")
graph.add_edge("count_words", "make_uppercase")
graph.add_edge("make_uppercase", END)

app = graph.compile()

result = app.invoke({"message": "hello my name is Tanish"})
print(result)
