import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.1-8b-instant"
)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
# -----------------------------------
# Supervisor Agent
# -----------------------------------

def supervisor_node(state: State):

    # Supervisor system prompt
    system_prompt = SystemMessage(
        content="""
        You are a supervisor agent.

        Your job is to decide which specialized agent
        should handle the user's request.

        Available agents:
        - billing_agent -> billing, payments, invoices, refunds
        - technical_agent -> bugs, errors, APIs, integrations, code
        - general_agent -> everything else

        Return ONLY one of:
        billing_agent
        technical_agent
        general_agent
        """
    )

    response = llm.invoke(
    [system_prompt] + state["messages"]
    )

    next_agent = "general_agent" # default agent
    
    for agent in [
    "billing_agent",
    "technical_agent",
    "general_agent"
    ]:
        if agent in response.content:
            next_agent = agent
            break


    return {"next_agent": next_agent}

# -----------------------------------
# Billing Agent
# -----------------------------------

def billing_agent(state: State):

    system_prompt = SystemMessage(
        content="""
        You are a billing support specialist.

        Help users with:
        - invoices
        - refunds
        - subscription plans
        - payment failures
        - billing history

        Be concise and professional.
        """
    )

    response = llm.invoke(
        [system_prompt] + state["messages"]
    )

    return {
        "messages": [response]
    }


# -----------------------------------
# Technical Agent
# -----------------------------------

def technical_agent(state: State):

    system_prompt = SystemMessage(
        content="""
        You are a technical support engineer.

        Help users with:
        - bugs
        - APIs
        - integrations
        - authentication
        - coding errors
        - debugging

        Give technical and accurate answers.
        """
    )

    response = llm.invoke(
        [system_prompt] + state["messages"]
    )

    return {
        "messages": [response]
    }


# -----------------------------------
# General Agent
# -----------------------------------

def general_agent(state: State):

    system_prompt = SystemMessage(
        content="""
        You are a helpful customer support assistant.

        Handle:
        - general questions
        - product information
        - greetings
        - non-technical conversations

        Be friendly and helpful.
        """
    )

    response = llm.invoke(
        [system_prompt] + state["messages"]
    )

    next_agent = response.content.strip()

    # Fallback extraction
    for agent in [
        "billing_agent",
        "technical_agent",
        "general_agent"
    ]:
        if agent in next_agent:
            next_agent = agent
            break
    

    return {
        "messages": [response]
    }



def route_to_agent(state: State) -> str:
    return state["next_agent"]

graph = StateGraph(State)
graph.add_node("supervisor", supervisor_node)
graph.add_node("billing_agent", billing_agent)
graph.add_node("technical_agent", technical_agent)
graph.add_node("general_agent", general_agent)
graph.add_edge(START, "supervisor") # the graph starts with the supervisor node, which decides which agent should handle the request based on the initial messages
graph.add_conditional_edges(
    "supervisor", 
    route_to_agent,
    {
    "billing_agent": "billing_agent",
    "technical_agent": "technical_agent",
    "general_agent": "general_agent"
    }
)

graph.add_edge("billing_agent", END) # after the billing agent processes the messages, we end the graph execution and return the billing agent's response
graph.add_edge("technical_agent", END) # after the technical agent processes the messages, we
graph.add_edge("general_agent", END) # after the general agent processes the messages, we end the graph execution and return the general agent's response

graph_app = graph.compile()
result = graph_app.invoke({"messages": [HumanMessage(content="I'm getting a 401 error on your API")]})
print(result)