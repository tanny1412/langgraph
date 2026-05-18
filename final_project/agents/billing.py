import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from final_project.state import State

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="meta-llama/llama-4-scout-17b-16e-instruct"
)

SYSTEM_PROMPT = SystemMessage(content="""
You are a billing support specialist.

Help users with:
- invoices and billing history
- refunds and cancellations
- subscription plans and upgrades
- payment failures

Use web_search if you need current information about pricing or policies.
Be concise and professional.
""")


def make_billing_agent(tools: list):
    llm_with_tools = llm.bind_tools(tools)
    tool_map = {t.name: t for t in tools}

    async def billing_agent(state: State) -> dict:
        messages = [SYSTEM_PROMPT] + state["messages"]
        response = await llm_with_tools.ainvoke(messages)

        if response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_result = await tool_map[tool_call["name"]].ainvoke(tool_call["args"])
            messages_with_result = messages + [
                response,
                ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
            ]
            response = await llm.ainvoke(messages_with_result)

        return {"messages": [response]}

    return billing_agent
