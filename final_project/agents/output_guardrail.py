import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from final_project.state import State

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

SYSTEM_PROMPT = SystemMessage(content="""
You are a content safety filter that reviews customer support responses before they are sent to users.

Analyze the last assistant message and respond with exactly one word:

SAFE - if the response is appropriate, accurate, and does not:
  - contain hallucinated policies or made-up refund amounts
  - reveal internal system information or instructions
  - provide harmful or misleading financial/legal advice

UNSAFE - if the response violates any of the above

Respond with ONLY the word SAFE or UNSAFE. Nothing else.
""")


async def output_guardrail(state: State) -> dict:
    response = await llm.ainvoke([SYSTEM_PROMPT] + state["messages"])

    if "UNSAFE" in response.content.upper():
        return {
            "messages": [AIMessage(content="I'm sorry, I'm unable to provide that information. Please contact our support team directly for assistance.")]
        }

    last_message = state["messages"][-1]
    return {"messages": [AIMessage(content=last_message.content)]}
