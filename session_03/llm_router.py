import os
from typing import TypedDict
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


class State(TypedDict):
    question: str
    answer: str

def router(state: State) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=10,
        messages=[
            {"role": "system", "content": "You are a router. Given a question, reply with ONLY one word — either 'database' or 'simple'. No explanation, no punctuation, just the word."},
            {"role": "user", "content": state["question"]}
        ]
    )
    
    return response.choices[0].message.content.strip()

def answer_simple(state: State) -> dict:
    return {"answer": "I answered from my knowledge base!"}

def answer_database(state: State) -> dict:
    return {"answer": "I answered from the database!"}

graph = StateGraph(State)
graph.add_node("database_node", answer_database)
graph.add_node("simple_node", answer_simple)

graph.add_conditional_edges(START,
                            router,
                            {"simple" : "simple_node",
                             "database" : "database_node"})

graph.add_edge("simple_node", END)
graph.add_edge("database_node", END)

app = graph.compile()

result = app.invoke({"question": "What is our employees records database name?"})
print(result)
