import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langsmith import Client
from langsmith.evaluation import evaluate
from final_project.agents.billing import make_billing_agent
from final_project.rag.knowledge_base import build_knowledge_base, search_docs
from final_project.state import State

load_dotenv()

vectorstore = build_knowledge_base()

@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal billing knowledge base for policy information."""
    return search_docs(query, vectorstore)

DATASET_NAME = "billing-agent-quality-eval"

TEST_CASES = [
    {
        "message": "What is your refund policy?",
        "criteria": "Response must mention 30 days refund window and 5-7 business days processing time."
    },
    {
        "message": "How do I cancel my subscription?",
        "criteria": "Response must mention that cancellation takes effect at end of current billing period and no partial refunds."
    },
    {
        "message": "I was charged twice this month, what can I do?",
        "criteria": "Response must mention billing dispute process, 60 day window to submit dispute, and that duplicate charges are automatically refunded."
    },
    {
        "message": "What payment methods do you accept?",
        "criteria": "Response must mention at least two of: Visa, Mastercard, American Express, PayPal."
    },
    {
        "message": "I want to upgrade my plan mid-month, will I be charged immediately?",
        "criteria": "Response must mention prorated charge for remainder of billing cycle."
    },
]

judge_llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o-mini"
)

JUDGE_PROMPT = """You are evaluating a customer support response.

Question: {question}
Response: {response}
Criteria: {criteria}

Does the response satisfy the criteria? Score from 0 to 1:
1.0 = fully satisfies criteria
0.5 = partially satisfies criteria
0.0 = does not satisfy criteria

Respond with ONLY a number: 0.0, 0.5, or 1.0"""


def create_dataset(client: Client) -> None:
    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' already exists, skipping creation.")
        return

    dataset = client.create_dataset(DATASET_NAME)
    client.create_examples(
        inputs=[{"message": tc["message"]} for tc in TEST_CASES],
        outputs=[{"criteria": tc["criteria"]} for tc in TEST_CASES],
        dataset_id=dataset.id,
    )
    print(f"Created dataset '{DATASET_NAME}' with {len(TEST_CASES)} examples.")


async def run_billing_agent(inputs: dict) -> dict:
    state = State(messages=[HumanMessage(content=inputs["message"])], next_agent="billing_agent")
    agent = make_billing_agent([search_knowledge_base])
    result = await agent(state)
    messages = result.get("messages", [])
    last_message = messages[-1] if messages else None
    return {"response": last_message.content if last_message else ""}


def llm_judge(outputs: dict, reference_outputs: dict) -> dict:
    prompt = JUDGE_PROMPT.format(
        question=outputs.get("message", ""),
        response=outputs["response"],
        criteria=reference_outputs["criteria"]
    )
    result = judge_llm.invoke([SystemMessage(content=prompt)])
    try:
        score = float(result.content.strip())
    except ValueError:
        score = 0.0
    return {"key": "response_quality", "score": score}


def target(inputs: dict) -> dict:
    result = asyncio.run(run_billing_agent(inputs))
    result["message"] = inputs["message"]
    return result


if __name__ == "__main__":
    client = Client()
    create_dataset(client)

    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[llm_judge],
        experiment_prefix="billing-quality",
    )

    scores = [r["evaluation_results"]["results"][0].score for r in results]
    avg = sum(scores) / len(scores)
    print(f"\nBilling agent quality: {avg:.1%} average score ({len(scores)} examples)")
