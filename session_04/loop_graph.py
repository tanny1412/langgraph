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
    quality: str
    attempts: int


def answer_node(state: State) -> dict:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=200,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer the question clearly and concisely"},
            {"role": "user", "content": state["question"]}
        ]
    )
    
    return {"answer": response.choices[0].message.content.strip()}

def critic_node(state: State) -> dict:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=200,
        messages=[
            {"role": "system", "content": "You are a critic. Given a question and an answer, rate the quality of the answer as either 'good' or 'bad'. Just the word, nothing else.  This is what makes an answer good:   - Directly answers the question \
  - At least 2 sentences \
  - Factually reasonable "},
            {"role": "user", "content": f"Question: {state['question']}\nAnswer: {state['answer']}"}
        ]
    )
    
    return {"quality": response.choices[0].message.content.strip().lower(),
            "attempts": state["attempts"] + 1}
    
def should_retry(state: State) -> str:
    if state["quality"] == "good":
        return "end"
    elif state["attempts"] >= 3:
        return "end"
    else:
        return "answer_node"
    

graph = StateGraph(State)
graph.add_node("answer_node", answer_node)
graph.add_node("critic_node", critic_node)

graph.add_edge(START, "answer_node")
graph.add_edge("answer_node", "critic_node")
graph.add_conditional_edges("critic_node", should_retry, {"answer_node": "answer_node",
                                                           "end": END})

app = graph.compile()

result = app.invoke({"question": "What is the meaning of life?", "attempts": 0})
print(result)