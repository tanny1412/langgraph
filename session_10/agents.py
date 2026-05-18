import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from session_10.state import State

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.1-8b-instant"
)


async def agent_node(state: State):
    full_response = None
    async for token in llm.astream(state["messages"]):
        if full_response is None:
            full_response = token
        else:
            full_response = full_response + token
    return {"messages": [full_response]}
