import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from final_project.state import State

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.1-8b-instant"
)

SYSTEM_PROMPT = SystemMessage(content="""
You are a friendly customer support assistant.

Handle:
- greetings and general questions
- product information
- anything that isn't billing or technical

Be warm, helpful, and concise.
""")


async def general_agent(state: State) -> dict:
    response = await llm.ainvoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}
