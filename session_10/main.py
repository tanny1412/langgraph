from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from session_10.graph import graph_builder


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSqliteSaver.from_conn_string("session_10/conversations.db") as checkpointer:
        app.state.graph = graph_builder.compile(checkpointer=checkpointer)
        yield


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    thread_id: str


@app.post("/chat")
async def chat(request: ChatRequest, http_request: Request):
    graph_app = http_request.app.state.graph
    config = {"configurable": {"thread_id": request.thread_id}}

    async def event_stream():
        async for event in graph_app.astream(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
            stream_mode="updates"
        ):
            for _, updates in event.items():
                for msg in updates.get("messages", []):
                    yield f"data: {msg.content}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/history/{thread_id}")
async def get_history(thread_id: str, http_request: Request):
    graph_app = http_request.app.state.graph
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph_app.aget_state(config)
    messages = []
    for msg in state.values.get("messages", []):
        messages.append({
            "role": "human" if isinstance(msg, HumanMessage) else "assistant",
            "content": msg.content
        })
    return {"thread_id": thread_id, "messages": messages}
