import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langsmith import Client
from langsmith.evaluation import evaluate
from final_project.agents.supervisor import supervisor_node
from final_project.state import State

load_dotenv()

DATASET_NAME = "supervisor-routing-eval"

TEST_CASES = [
    {"message": "I need a refund for my order", "expected": "billing_agent"},
    {"message": "My invoice shows the wrong amount", "expected": "billing_agent"},
    {"message": "I was charged twice this month", "expected": "billing_agent"},
    {"message": "How do I cancel my subscription?", "expected": "billing_agent"},
    {"message": "I want to upgrade my plan", "expected": "billing_agent"},
    {"message": "My payment keeps getting declined", "expected": "billing_agent"},
    {"message": "Where is my billing history?", "expected": "billing_agent"},
    {"message": "My API keeps returning a 401 error", "expected": "technical_agent"},
    {"message": "The integration with Slack is broken", "expected": "technical_agent"},
    {"message": "I'm getting a null pointer exception in your SDK", "expected": "technical_agent"},
    {"message": "Authentication is not working", "expected": "technical_agent"},
    {"message": "How do I set up webhooks?", "expected": "technical_agent"},
    {"message": "My app crashes when I call the search endpoint", "expected": "technical_agent"},
    {"message": "What does error code 500 mean in your API?", "expected": "technical_agent"},
    {"message": "Hello, I need some help", "expected": "general_agent"},
    {"message": "What are your business hours?", "expected": "general_agent"},
    {"message": "What features does your product have?", "expected": "general_agent"},
    {"message": "How long have you been in business?", "expected": "general_agent"},
    {"message": "Do you have a mobile app?", "expected": "general_agent"},
    {"message": "Can you tell me about your pricing plans?", "expected": "general_agent"},
]


def create_dataset(client: Client) -> None:
    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' already exists, skipping creation.")
        return

    dataset = client.create_dataset(DATASET_NAME)
    client.create_examples(
        inputs=[{"message": tc["message"]} for tc in TEST_CASES],
        outputs=[{"expected": tc["expected"]} for tc in TEST_CASES],
        dataset_id=dataset.id,
    )
    print(f"Created dataset '{DATASET_NAME}' with {len(TEST_CASES)} examples.")


async def run_supervisor(inputs: dict) -> dict:
    state = State(messages=[HumanMessage(content=inputs["message"])], next_agent="")
    result = await supervisor_node(state)
    return {"next_agent": result["next_agent"]}


def routing_accuracy(outputs: dict, reference_outputs: dict) -> dict:
    correct = outputs["next_agent"] == reference_outputs["expected"]
    return {"key": "routing_correct", "score": 1 if correct else 0}


def target(inputs: dict) -> dict:
    return asyncio.run(run_supervisor(inputs))


if __name__ == "__main__":
    client = Client()
    create_dataset(client)

    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[routing_accuracy],
        experiment_prefix="supervisor-routing",
    )

    scores = [r["evaluation_results"]["results"][0].score for r in results]
    accuracy = sum(scores) / len(scores)
    print(f"\nRouting accuracy: {accuracy:.0%} ({sum(scores)}/{len(scores)} correct)")
