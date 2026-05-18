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
You are a customer support supervisor.

Your job is to decide which specialist should handle the user's request.

Available agents:
- billing_agent  → invoices, refunds, payments, subscriptions, billing history
- technical_agent → bugs, errors, APIs, integrations, authentication, code
- general_agent  → greetings, product info, everything else

Return ONLY one of:
billing_agent
technical_agent
general_agent
""")


async def supervisor_node(state: State) -> dict:
    response = await llm.ainvoke([SYSTEM_PROMPT] + state["messages"])

    next_agent = "general_agent"
    for agent in ["billing_agent", "technical_agent", "general_agent"]:
        if agent in response.content:
            next_agent = agent
            break

    return {"next_agent": next_agent}
