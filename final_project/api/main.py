from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from final_project.graph import build_graph


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with streamable_http_client("http://mcp-server:8080/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            async with AsyncPostgresSaver.from_conn_string("postgresql://tanish:password@postgres:5432/langgraph") as checkpointer:
                await checkpointer.setup()
                graph = build_graph(tools)
                app.state.graph = graph.compile(checkpointer=checkpointer)
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
                    if msg.content:
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
