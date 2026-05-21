from langgraph.graph import StateGraph, START, END
from final_project.state import State
from final_project.agents.supervisor import supervisor_node
from final_project.agents.general import general_agent
from final_project.agents.billing import make_billing_agent
from final_project.agents.technical import make_technical_agent
from final_project.agents.guardrail import input_guardrail
from final_project.agents.output_guardrail import output_guardrail


def route_after_guardrail(state: State) -> str:
    return state["next_agent"]


def route_to_agent(state: State) -> str:
    return state["next_agent"]


def build_graph(billing_tools: list, technical_tools: list):
    graph = StateGraph(State)

    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("billing_agent", make_billing_agent(billing_tools))
    graph.add_node("output_guardrail", output_guardrail)
    graph.add_node("technical_agent", make_technical_agent(technical_tools))
    graph.add_node("general_agent", general_agent)

    graph.add_edge(START, "input_guardrail")
    graph.add_conditional_edges(
        "input_guardrail",
        route_after_guardrail,
        {
            "allowed": "supervisor",
            "blocked": END,
        }
    )
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "billing_agent": "billing_agent",
            "technical_agent": "technical_agent",
            "general_agent": "general_agent",
        }
    )
    graph.add_edge("billing_agent", "output_guardrail")
    graph.add_edge("output_guardrail", END)
    graph.add_edge("technical_agent", END)
    graph.add_edge("general_agent", END)

    return graph
