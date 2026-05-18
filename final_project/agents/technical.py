import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from final_project.state import State

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

SYSTEM_PROMPT = SystemMessage(content="""
You are a technical support engineer.

Help users with:
- bugs and error messages
- API usage and integrations
- authentication issues
- debugging and troubleshooting

Use web_search to find current documentation, error solutions, or known issues.
Give accurate, technical answers.
""")


def make_technical_agent(tools: list):
    llm_with_tools = llm.bind_tools(tools)
    tool_map = {t.name: t for t in tools}

    async def technical_agent(state: State) -> dict:
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

    return technical_agent
