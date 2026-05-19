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

    async with streamable_http_client("http://billing-mcp-server:8081/mcp") as (b_read, b_write, _):
        async with ClientSession(b_read, b_write) as billing_session:
            await billing_session.initialize()
            billing_tools = await load_mcp_tools(billing_session)

            async with streamable_http_client("http://technical-mcp-server:8082/mcp") as (t_read, t_write, _):
                async with ClientSession(t_read, t_write) as technical_session:
                    await technical_session.initialize()
                    technical_tools = await load_mcp_tools(technical_session)

                    async with AsyncPostgresSaver.from_conn_string("postgresql://tanish:password@postgres:5432/langgraph") as checkpointer:
                        await checkpointer.setup()
                        graph = build_graph(billing_tools, technical_tools)
                        app.state.graph = graph.compile(checkpointer=checkpointer, interrupt_after=["billing_agent"])
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
        try:
            async for event in graph_app.astream(
                {"messages": [HumanMessage(content=request.message)]},
                config=config,
                stream_mode="updates"
            ):
                for _, updates in event.items():
                    for msg in updates.get("messages", []):
                        if msg.content:
                            yield f"data: {msg.content}\n\n"
        except Exception:
            history = [s async for s in graph_app.aget_state_history(config)]
            if len(history) > 0:
                last_good = history[0]
                retry_config = {
                    "configurable": {
                        "thread_id": request.thread_id,
                        "checkpoint_id": last_good.config["configurable"]["checkpoint_id"]
                    }
                }
                try:
                    result = await graph_app.ainvoke(None, retry_config)
                    messages = result["messages"] if isinstance(result, dict) else result[0]["messages"]
                    last_msg = messages[-1]
                    if last_msg.content:
                        yield f"data: {last_msg.content}\n\n"
                except Exception:
                    yield "data: Something went wrong. Please try again.\n\n"
            else:
                yield "data: Something went wrong. Please try again.\n\n"

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

@app.post("/approve/{thread_id}")
async def approve(thread_id: str, http_request: Request):
    graph_app = http_request.app.state.graph
    config = {"configurable": {"thread_id": thread_id}}
    await graph_app.ainvoke(None, config=config)
    return {"status": "approved"}

