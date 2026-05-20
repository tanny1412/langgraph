from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

DOCS = [
    Document(
        page_content="Refund Policy: Customers can request a refund within 30 days of purchase. Refunds are processed back to the original payment method within 5-7 business days. Digital products are non-refundable after download.",
        metadata={"source": "refund_policy"}
    ),
    Document(
        page_content="Subscription Cancellation: Customers may cancel their subscription at any time. Cancellation takes effect at the end of the current billing period. No partial refunds are given for unused subscription time.",
        metadata={"source": "subscription_policy"}
    ),
    Document(
        page_content="Billing Disputes: If a customer believes they were incorrectly charged, they must submit a dispute within 60 days of the charge. Disputes are reviewed within 3 business days. Duplicate charges are automatically refunded.",
        metadata={"source": "billing_disputes"}
    ),
    Document(
        page_content="Payment Methods: We accept Visa, Mastercard, American Express, and PayPal. Payments are processed securely via Stripe. Failed payments are retried automatically after 3 days.",
        metadata={"source": "payment_methods"}
    ),
    Document(
        page_content="Upgrade and Downgrade Policy: Customers can upgrade their plan at any time and are charged a prorated amount for the remainder of the billing cycle. Downgrades take effect at the next billing cycle.",
        metadata={"source": "plan_changes"}
    ),
]


def build_knowledge_base() -> Chroma:
    embeddings = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"))
    vectorstore = Chroma.from_documents(DOCS, embeddings)
    return vectorstore


def search_docs(query: str, vectorstore: Chroma) -> str:
    results = vectorstore.similarity_search(query, k=2)
    return "\n\n".join([doc.page_content for doc in results])
