# Dev Logs — Questions, Doubts & Discoveries

A running log of every question, doubt, or interesting thing that comes up.
Come back here when something clicks later — or when it still doesn't.

---

## Format

```
### [Session X] — Short title of the question
**Q:** The actual question or doubt
**Status:** open / answered / partially answered
**Answer (if known):** ...
**Came up on:** date
```

---

## Pre-Session — Conceptual Questions

### [Pre-Session] — Can LangChain do any decision-making at all?
**Q:** If LangChain is linear, can it do *any* routing or branching?
**Status:** answered
**Answer:** Yes — you can add conditional Python logic inside a chain. But the *graph structure* (which step connects to which) is fixed when you write the code. LangGraph lets the LLM's output decide the structure at runtime.
**Came up on:** 2026-05-13

### [Pre-Session] — Where does conversation memory live when calling an LLM directly?
**Q:** When you call Claude/OpenAI and want it to remember earlier messages, where does that list live?
**Status:** answered
**Answer:** In a plain Python list you manage yourself. The API is stateless — every call is fresh. You send the full message history each time. LangGraph puts this list inside state and manages it for you automatically.
**Came up on:** 2026-05-13

### [Pre-Session] — Does state live in a database by default?
**Q:** Is state persisted to a database automatically after every update?
**Status:** answered
**Answer:** No — by default state lives only in Python memory and dies when the process stops. The database part (checkpointer) is an explicit addition covered in Session 7.
**Came up on:** 2026-05-13

---

## Session 1 — State + Nodes

### [Session 1] — Nodes return partial state, not full state
**Q:** If a node only returns one key, what happens to the rest of the state?
**Status:** answered
**Answer:** LangGraph merges the return value into the existing state. Other fields survive untouched. This is the opposite of normal Python functions where you get back exactly what you return.
**Came up on:** 2026-05-13

### [Session 1] — Why TypedDict and not a plain dict?
**Q:** Why does LangGraph use TypedDict for state instead of a regular Python dict?
**Status:** answered
**Answer:** Plain dicts allow silent bugs — typos in key names, wrong types, unexpected new keys. TypedDict creates a contract: every node knows exactly what fields exist and what types they are. Type checkers catch mistakes before runtime. Critical in team codebases.
**Came up on:** 2026-05-13

---

## Session 4 — Loops + Termination

### [Session 4] — Should every node have a critic?
**Q:** In a long pipeline, does every answer node need a critic after it?
**Status:** answered
**Answer:** No — critics are expensive (time + money). Use them selectively: high-stakes outputs (customer-facing, legal, financial) yes. Internal routing, simple lookups — no. One critic at the exit gate is usually enough. Rule: critic only where quality variance actually matters.
**Came up on:** 2026-05-14

### [Session 4] — Where to increment attempts — answer_node or critic_node?
**Q:** Should attempts be incremented in answer_node or critic_node?
**Status:** answered
**Answer:** Either works, but answer_node is semantically cleaner — attempts means "how many answers have been generated." The key rule is: increment exactly once per loop cycle, before the termination check reads it.
**Came up on:** 2026-05-14

### [Session 4] — Why does the critic retry on simple tasks?
**Q:** Why is the critic saying "bad" on perfectly good answers, causing unnecessary retries?
**Status:** answered
**Answer:** Vague prompt — "rate as good or bad" gives the LLM no criteria, so it decides inconsistently. Fix: give the critic explicit checklist (min length, directly addresses question, factually reasonable). After fixing — dropped from 2-3 attempts to 1 consistently. Prompt quality directly determines system cost and reliability in production.
**Came up on:** 2026-05-14

### [Session 4] — Why does attempts vary between runs?
**Q:** Sometimes attempts is 2, sometimes 3. Why?
**Status:** answered
**Answer:** LLMs are non-deterministic. The critic may approve on the first, second, or third try. The max_retries cap (3) is the safety net — guarantees the graph always terminates even if the critic never approves.
**Came up on:** 2026-05-14

---

## Session 7 — Persistence & Memory

### [Session 7] — thread_id and multi-user conversations
**Q:** How do multiple users have isolated conversations with the same graph?
**Status:** answered
**Answer:** thread_id namespaces each conversation. Same graph, different thread_id = different user's isolated history. In production thread_id = f"{user_id}_{session_id}" — user_id from auth system (JWT), session_id from frontend (UUID). One session = one conversation. User starts new chat = new session_id = new thread. The graph never generates identity — the API layer does.
**Came up on:** 2026-05-14

### [Session 7] — Why does persistence matter?
**Q:** Why can't we just keep state in memory?
**Status:** answered
**Answer:** Memory dies when the process stops. For a customer support chatbot, user has to re-explain their issue after every restart. For long-running workflows (legal review, document processing) a server crash loses all progress. Persistence = conversations survive restarts, workflows resume from last checkpoint. Every real production AI system needs this.
**Came up on:** 2026-05-14

### [Session 7] — Does the LLM read from conversations.db directly?
**Q:** Does llm.invoke() look at conversations.db and load history itself?
**Status:** answered
**Answer:** No — the LLM is stateless and has no idea the database exists. LangGraph's checkpointer does all the work: on invoke it loads the full state snapshot for that thread_id, merges it with the new message using add_messages, then calls llm.invoke() with the complete messages list. The LLM just sees a normal conversation history. The checkpointer is invisible to it.
**Came up on:** 2026-05-14

### [Session 7] — How do you actually implement auto-retry from a checkpoint?
**Q:** If an agent fails mid-workflow, how do you write the code to roll back and retry from the last good checkpoint?
**Status:** answered
**Answer:** Write a wrapper around graph_app.invoke(). On exception: call get_state_history(config) — returns all checkpoints newest-first. Index 0 = failed state, index 1 = last good state. Extract its checkpoint_id, build a new config with that checkpoint_id, call invoke(None, retry_config) — None means "resume, don't add new input." LangGraph replays from that exact point. This is not built-in — it's your code on top of the persistence layer. See LEARNING_PLAN.md Future Work section.
**Came up on:** 2026-05-14

### [Session 7] — Does rollback after agent failure happen automatically?
**Q:** If we use PostgresSaver and an agent fails mid-workflow, does it automatically roll back and retry from the last good checkpoint?
**Status:** answered
**Answer:** No — two separate concerns. PostgresSaver automatically saves a checkpoint after every node (free, no code needed). But rollback + retry is logic you write: catch the exception, query checkpoints for the last good one, explicitly resume from that checkpoint_id. LangGraph gives you the tools, not the decision. Like Postgres transaction logs — it writes every change automatically, but ROLLBACK is still a command you issue.
**Came up on:** 2026-05-14

### [Session 7] — How do companies track agent success/failure in production?
**Q:** Where does failure vs success get stored — does the checkpointer track it?
**Status:** answered
**Answer:** The checkpointer only saves state snapshots — no concept of success or failure. Pattern: add a `status` field to State ("running" / "failed" / "completed"), each node updates it before returning, checkpoint carries it automatically. A separate monitoring job queries Postgres for thread_ids where status = "failed" and alerts or auto-retries. The full observability layer (dashboards, failure traces, step-by-step replay) is LangSmith — covered in Session 11.
**Came up on:** 2026-05-14

### [Session 7] — How does the checkpointer table actually look in production?
**Q:** In production, does the DB overwrite the row for a thread_id or append new rows?
**Status:** answered
**Answer:** Appends — one row per checkpoint, not one row per thread. Every state change creates a new checkpoint row with an incrementing checkpoint_id. On restore, LangGraph grabs the latest checkpoint for that thread_id. Why append? Time-travel: you can roll back to any checkpoint_id and resume from there — same feature as ChatGPT's "edit message and branch from here." Companies use this for debugging agent failures mid-workflow without restarting from zero. In prod: swap SqliteSaver for PostgresSaver, same API.
**Came up on:** 2026-05-14

---

## Session 6 — Multi-Agent Coordination

### [Session 6] — LLMs don't follow exact formatting instructions reliably
**Q:** The supervisor returned a full sentence instead of just "billing_agent". How do we handle this in production?
**Status:** answered
**Answer:** Always validate and extract — never trust exact formatting. Set a safe default first (general_agent), then loop through valid values and overwrite if found. This is the belt-and-suspenders approach. Production-grade solution is Pydantic structured output which enforces schema at API level — zero deviation possible.
**Came up on:** 2026-05-14

### [Session 6] — Supervisor vs Router — what's the difference?
**Q:** How is a supervisor agent different from a router?
**Status:** answered
**Answer:** Router: reads state, returns a string, one decision, disappears. Supervisor: full agent — maintains context, can chain multiple agents, synthesize results, loop. Router = traffic cop. Supervisor = project manager. Rule: start with a router, upgrade to supervisor only when you need orchestration.
**Came up on:** 2026-05-14

### [Session 6] — Why multiple agents instead of one?
**Q:** Why not just have one powerful agent handle everything?
**Status:** answered
**Answer:** One agent doing everything gets confused — its context fills with unrelated information. Multiple agents = each has a focused context window, specialized tools, and a specific system prompt for their domain. Billing agent knows billing, technical agent knows debugging. Like hiring specialists instead of one generalist. A supervisor agent routes questions to the right specialist.
**Came up on:** 2026-05-14

---

## Session 5.5 — MCP (Model Context Protocol)

### [Session 5.5] — How many API calls happen in a tool use loop?
**Q:** How many actual API calls happened in the MCP session?
**Status:** answered
**Answer:** 4 LLM calls to Groq + 3 MCP tool calls (local, free). Token count grew each call: 267 → 320 → 375 → 448 — full history resent every loop. A 3-tool-call question costs 4x the tokens of a direct answer. At scale this multiplies fast. Companies set max_tool_calls limits and write tight docstrings to stop the LLM searching multiple times. Fake search returning same result caused 3 retries — LLM kept trying different queries hoping for different results.
**Came up on:** 2026-05-14

### [Session 5.5] — async with, await, and concurrent connections — full mental model
**Q:** Why async? Why does it matter for MCP connections?
**Status:** answered
**Answer:** async with opens a non-blocking connection. In a FastAPI server with 100 users, each user needs an MCP connection. Sync would queue them — user 2 waits for user 1's connection to open. async with means all 100 connections open in parallel. Same for LLM calls and tool calls inside the graph — every I/O operation yields control to other users. ainvoke() runs the whole graph without blocking. Rule: anything that talks to network or subprocess needs await.
**Came up on:** 2026-05-14

### [Session 5.5] — Production MCP architecture
**Q:** How does this work at company scale with FastAPI?
**Status:** answered
**Answer:** Agent code runs behind FastAPI. MCP server runs separately (local stdio or hosted HTTP/SSE). FastAPI handles concurrent user requests, each user async-connects to the MCP server, all tool calls and LLM calls are non-blocking. Users don't wait for each other. This is the full production pattern.
**Came up on:** 2026-05-14

### [Session 5.5] — What problem does MCP solve?
**Q:** Why not just keep writing tool functions in the codebase?
**Status:** answered
**Answer:** Two problems: (1) every tool must exist as a Python function in your codebase — you maintain it. (2) not reusable across projects — other teams copy-paste. MCP fixes this: tools live on a server, agents connect as clients and discover tools automatically. One team maintains the Jira MCP server, every agent just connects. No duplication.
**Came up on:** 2026-05-14

### [Session 5.5] — What does transport="stdio" mean?
**Q:** What is stdio transport in MCP?
**Status:** answered
**Answer:** stdio = standard input/output. Two processes communicate through stdin/stdout pipes. Client launches the server as a subprocess, they talk through terminal streams. No network, no HTTP, no ports. For hosted company servers you'd switch to transport="sse" (HTTP). Same tools, different channel.
**Came up on:** 2026-05-14

### [Session 5.5] — Why so many MCP client imports?
**Q:** What are ClientSession, StdioServerParameters, stdio_client, and load_mcp_tools?
**Status:** answered
**Answer:** StdioServerParameters = config telling client which server file to launch (server.py). ClientSession = the active connection (like a DB connection). stdio_client = local transport layer, launches server as subprocess via stdin/stdout. load_mcp_tools = bridge between MCP and LangChain — discovers tools from server and converts them to LangChain @tool format so you can pass them to bind_tools and ToolNode. For remote servers use sse_client instead of stdio_client.
**Came up on:** 2026-05-14

### [Session 5.5] — How does MCP work in a company at scale?
**Q:** If I build an MCP server locally, how does my whole company use the same tools?
**Status:** answered
**Answer:** Local MCP server = only you. Hosted MCP server = whole company. DevOps hosts it on a server/container, exposes it over HTTP (SSE or HTTP transport). Every agent points to that URL. Tool updates happen in one place, everyone gets them automatically — no code changes in any agent codebase. This is the production MCP pattern.
**Came up on:** 2026-05-14

### [Session 5.5] — Claude Code itself uses MCP
**Q:** Is Claude Code using MCP right now?
**Status:** answered
**Answer:** Yes. Claude Code is an MCP client. Every tool call (Read, Edit, Bash, Write) is a tool living on an MCP server that Claude Code connects to on startup. When Claude reads a file in this conversation, it's calling the Read tool via MCP. You're learning to build exactly what you're using right now.
**Came up on:** 2026-05-14

### [Session 5.5] — Who runs the MCP server vs client?
**Q:** Does the agent run the MCP server?
**Status:** answered
**Answer:** No — two separate processes. MCP server runs separately (could be another team, third-party, or local). MCP client lives in your agent code and connects to the server. Claude Code is an MCP client — it connects to servers that expose file/code/search tools. You didn't write those tools, you just connected.
**Came up on:** 2026-05-14

---

## Session 5 — Tool Use

### [Session 5] — What is the difference between a node and an agent?
**Q:** When do we call something a node vs an agent?
**Status:** answered
**Answer:** All agents are nodes, not all nodes are agents. A node is any function that processes state. An agent is a node with an LLM inside that can decide to use tools. The LLM reasons about whether it needs more information before answering.
**Came up on:** 2026-05-14

### [Session 5] — Why Annotated[list, add_messages] and not just list?
**Q:** Why do we use Annotated with add_messages instead of just list for messages state?
**Status:** answered
**Answer:** Without add_messages, LangGraph overwrites the messages list on every state update — losing history. add_messages is a reducer that appends instead of replacing. Annotated is Python's way of attaching this merge strategy to the type hint. Pattern: Annotated[list, add_messages] — memorize it, it's in every production LangGraph codebase.
**Came up on:** 2026-05-14

### [Session 5] — How does the LLM know what tools exist?
**Q:** How do we tell the LLM what tools are available?
**Status:** answered
**Answer:** Tool name, description, and parameter types are passed in the API call as a schema. The LLM reads the docstring to decide whether to call the tool. Docstrings on tools are instructions for the LLM, not documentation for developers — bad docstrings = wrong tool usage.
**Came up on:** 2026-05-14

### [Session 5] — LLM constructs tool arguments, doesn't just copy user input
**Q:** Does the LLM just copy the user's message into the tool's query parameter?
**Status:** answered
**Answer:** No — the LLM reasons about what the best argument is based on the docstring and context. "Tell me about searching in LangGraph" → query="LangGraph search tools". Docstrings that guide argument construction ("use concise keyword-focused queries") directly improve tool call quality. This is context engineering for tools.
**Came up on:** 2026-05-14

### [Session 5] — Why pass tools to both bind_tools AND ToolNode?
**Q:** We pass the tools list to llm.bind_tools() AND ToolNode(). Why both?
**Status:** answered
**Answer:** bind_tools → sends tool schema to LLM so it can decide whether/what to call. ToolNode → has the actual Python functions to execute what the LLM decided. Decision and execution are separate. LLM decides, ToolNode executes. The AIMessage with tool_calls contains the tool name and args — ToolNode just matches and runs it.
**Came up on:** 2026-05-14

### [Session 5] — Message types in a tool call loop
**Q:** What are the message types in order during a tool call?
**Status:** answered
**Answer:** 1. HumanMessage (user question) → 2. AIMessage with tool_calls (LLM says "call this") → 3. ToolMessage (tool result) → 4. AIMessage (final answer, no tool calls). LLM sees full history on every loop. This is also why tool use is expensive — entire history resent each loop. Companies set tool call limits for cost control.
**Came up on:** 2026-05-14

### [Session 5] — How does the tool call loop work?
**Q:** Where does the decision to call a tool again (or stop) happen in the graph?
**Status:** answered
**Answer:** After agent node runs, a built-in router called tools_condition checks the last message. If it's a tool_call → goes to ToolNode → result added to messages → agent runs again. If it's a final text answer → END. You never write this loop manually — tools_condition handles it automatically.
**Came up on:** 2026-05-14

### [Session 5] — ChatOpenAI works with Groq?
**Q:** Can we use ChatOpenAI from langchain_openai with Groq's API?
**Status:** answered
**Answer:** Yes — Groq is OpenAI-compatible. Point ChatOpenAI at Groq's base_url and use the Groq API key. Same SDK, different server. This is why OpenAI-compatible APIs are valuable — one SDK works across providers.
**Came up on:** 2026-05-14

### [Session 5] — Pipeline vs Agent — when to use which?
**Q:** When does a company use a pipeline vs an agent?
**Status:** answered
**Answer:** Pipeline = fixed steps defined upfront, used for predictable tasks (summarization, classification). Agent = LLM decides its own steps at runtime, used for open-ended tasks (research, troubleshooting). The line: who controls the loop — you or the LLM?
**Came up on:** 2026-05-14

---

## Session 3 — LLM Node

### [Session 3] — Why use OpenAI SDK with Groq's API key?
**Q:** We're using the OpenAI client but pointing it at Groq. How does that work?
**Status:** answered
**Answer:** Groq built their API to be OpenAI-compatible — same request format, different server. You change base_url to point at Groq's servers and use your Groq API key. The SDK doesn't care who's on the other end. This is how companies swap LLM providers without touching business logic.
**Came up on:** 2026-05-13

### [Session 3] — LLM sometimes ignores instructions on first call
**Q:** The LLM routed incorrectly on the first run but correctly on the second. Why?
**Status:** answered
**Answer:** LLMs are non-deterministic. Even with tight instructions they can occasionally return unexpected output. In production you add output validation — check the return value and default to a safe path if it's not "simple" or "database". Structured output (Pydantic) solves this permanently — covered later.
**Came up on:** 2026-05-13

### [Session 3] — Why is Groq free?
**Q:** Why would Groq give their API for free?
**Status:** answered
**Answer:** Developer acquisition strategy — same as AWS/Vercel free tiers. Get developers hooked, charge enterprise customers for scale and reliability. Free tier has rate limits; production usage costs money.
**Came up on:** 2026-05-13

---

## Session 2 — Edges + Conditional Routing

### [Session 2] — What happens if you remove a key from State?
**Q:** Can you remove a key from the TypedDict State class?
**Status:** answered
**Answer:** You can, but the type checker will immediately flag every node that tries to read that key. Adding keys is the real danger — they silently float through the graph unused. Treat State changes like database schema changes: carefully, everyone must be aware.
**Came up on:** 2026-05-13

### [Session 2] — State class is the first thing to read in any graph codebase
**Q:** How do team members coordinate around State in a company?
**Status:** answered
**Answer:** State is the source of truth for the whole graph. In real projects it lives in its own state.py file. Any PR touching it gets extra scrutiny. Every team member reads it first before touching any node.
**Came up on:** 2026-05-13

### [Session 2] — add_edge vs add_conditional_edges
**Q:** What's the difference between add_edge and add_conditional_edges?
**Status:** answered
**Answer:** add_edge is a fixed/bold connection — always goes to that node. add_conditional_edges is a dashed/conditional connection — picks ONE next node based on what the router function returns. Using add_edge from a router creates a diamond that goes to ALL nodes, not one.
**Came up on:** 2026-05-13

### [Session 2] — Why does the router function return str and not dict?
**Q:** Router functions return a string, not a dict like regular nodes. Why?
**Status:** answered
**Answer:** Regular nodes update the whiteboard (return dict). Router functions don't update anything — their only job is to answer "where do I go next?" so they return a string that maps to the next node name.
**Came up on:** 2026-05-13

---

## Session 8 — Human-in-the-Loop

### [Session 8] — How does interrupt_after work?
**Q:** How do you pause a graph after a specific node?
**Status:** answered
**Answer:** Add `interrupt_after=["node_name"]` to `graph.compile()`. LangGraph automatically pauses after that node runs, saves state to the checkpointer, and returns control to your code. No pause logic needed in the node itself. The string must exactly match the name given in `add_node()`. It's a list — multiple nodes can be interrupted: `interrupt_after=["research", "critic"]` pauses after each one separately.
**Came up on:** 2026-05-14

### [Session 8] — What does invoke(None, config) do?
**Q:** Why do we pass None as input to invoke when resuming?
**Status:** answered
**Answer:** `None` = no new messages, just resume from the checkpoint. Contrast: `invoke({"messages": [...]}, config)` starts a new turn with fresh input. `invoke(None, config)` says "pick up exactly where you paused." LangGraph reads the checkpoint, finds where in the graph execution stopped, and continues from that point.
**Came up on:** 2026-05-14

### [Session 8] — How does LangGraph know where to resume in the graph?
**Q:** When invoke(None, config) is called, how does LangGraph know which node to continue from?
**Status:** answered
**Answer:** The checkpointer saves not just the state (messages) but also the graph execution position — which node just finished, what the next step was going to be. On resume, LangGraph reads the checkpoint and knows exactly where to pick up. You don't tell it — the checkpoint has that information already.
**Came up on:** 2026-05-14

### [Session 8] — In production, does the Python process wait during the pause?
**Q:** While the graph is paused waiting for human approval, is the Python process blocked?
**Status:** answered
**Answer:** No — in production there's no input() call. The first invoke() returns the paused state to your FastAPI endpoint, which returns it to the frontend. The Python process is free. The graph state lives in the DB. The pause can last minutes, hours, days. When the user clicks Approve, a new HTTP request comes in and calls invoke(None, config) — a completely separate process. This is why the checkpointer is essential for human-in-the-loop.
**Came up on:** 2026-05-14

### [Session 8] — What triggers the resume in production?
**Q:** In production, who calls invoke(None, config) — is it a custom frontend?
**Status:** answered
**Answer:** Three options: (1) your own frontend — Approve button calls a FastAPI /resume/{thread_id} endpoint which calls invoke(None, config). (2) LangGraph Platform — pre-built UI with pause/resume built in. (3) No UI — Slack/email bot posts "approve this?", human replies, webhook triggers invoke(None, config). The graph doesn't care how resume is triggered — it just waits for invoke(None, config) with the right thread_id.
**Came up on:** 2026-05-14

---

## Session 9 — Streaming

### [Session 9] — Two types of streaming and when to use each
**Q:** What's the difference between token streaming and event streaming?
**Status:** answered
**Answer:** Token streaming = LLM output word by word (typing effect for users). Event streaming = which node ran and what it returned (visibility into graph progress). Both can be user-facing — Perplexity shows "Searching sources..." while typing the answer. That's event streaming exposed to the user. In production both run simultaneously from the same `graph.stream()` loop. `stream_mode="updates"` = only what changed per node (production choice). `stream_mode="values"` = full state after every node (debugging).
**Came up on:** 2026-05-14

### [Session 9] — How token streaming works inside agent_node
**Q:** How do you collect streamed tokens and return them as a single message in state?
**Status:** answered
**Answer:** `llm.stream()` returns a generator of `AIMessageChunk` objects. Loop through them, concatenate using `+` (LangChain overrides `__add__` on AIMessageChunk to concatenate content — not plain Python). End result is one `AIMessageChunk` with the full text. Return it wrapped in a list for `add_messages`. In production use `llm.astream()` — same but async/non-blocking so 100 users can stream simultaneously.
**Came up on:** 2026-05-14

### [Session 9] — What does the FastAPI streaming endpoint actually look like?
**Q:** How does graph.stream() connect to a FastAPI endpoint that sends tokens to the frontend?
**Status:** answered
**Answer:** FastAPI uses StreamingResponse + SSE (Server-Sent Events). The endpoint loops through graph.stream() and yields each chunk in SSE format (`data: ...\n\n`). Frontend connects once and receives chunks as they arrive. thread_id comes from the request so each user gets their own conversation. Full shape:
```python
@app.post("/chat")
async def chat(message: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    async def event_stream():
        for event in graph.stream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="updates"
        ):
            yield f"data: {str(event)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```
Built properly in Session 10.
**Came up on:** 2026-05-14

### [Session 9] — In production, are agent nodes async?
**Q:** In production, do agent nodes use async def and astream instead of def and stream?
**Status:** answered
**Answer:** Yes. In production all agent nodes are `async def` and use `llm.astream()` with `async for`. Same concatenation logic, but non-blocking — 100 users can stream simultaneously without waiting for each other. The node itself doesn't change structurally, just `def` → `async def`, `stream` → `astream`, `for` → `async for`. The token concatenation logic with AIMessageChunk + stays identical.
**Came up on:** 2026-05-14

### [Session 9] — Where does streaming to the frontend actually happen?
**Q:** Does agent_node change in production to send tokens to the frontend?
**Status:** answered
**Answer:** No — agent_node stays exactly the same. What changes is the consumer of graph.stream(). In a script: `print(event)`. In production FastAPI endpoint: `yield event` which sends chunks to the frontend over SSE (Server-Sent Events). The node's job is to build full_response and return it to state. Streaming to the user happens at the FastAPI layer. LangSmith captures everything silently in the background via env variable — no manual logging needed.
**Came up on:** 2026-05-14

---

## Session 10 — FastAPI Integration

### [Session 10] — Full user flow: /history + /chat together
**Q:** Why do we need both /history and /chat? What do they achieve together?
**Status:** answered
**Answer:** Two different moments in a user's session. /history = user opens the app or refreshes — frontend hits GET /history/{thread_id}, loads full past conversation at once, renders the chat UI. /chat = user sends a message — frontend hits POST /chat, streams response token by token. Together they form a complete chat product. Think WhatsApp: opening an old chat = /history (load everything). Sending a message = /chat (live streaming). Always in this order: load history first, then stream new messages on top.
**Came up on:** 2026-05-14

### [Session 10] — Production patterns to remember (not lines)
**Q:** Do I need to memorize every line in main.py?
**Status:** answered
**Answer:** No — memorize the patterns, look up the lines. Three patterns that repeat in every production LangGraph + FastAPI app: (1) Lifespan = open shared resources at startup, store on app.state. (2) /chat = astream() + StreamingResponse + yield = live streaming to frontend. (3) /history = aget_state() + return clean JSON = load past conversation. state.values.get("messages", []) is the standard pattern for reading messages from a state snapshot — you'll see it everywhere.
**Came up on:** 2026-05-14

### [Session 10] — Full mental model of lifespan + app.state
**Q:** What is the full mental model of the lifespan pattern in FastAPI?
**Status:** answered
**Answer:** Use asynccontextmanager to run code on server startup. Open the DB connection once as checkpointer — shared across every request for all users — because opening/closing a connection per endpoint is slow and wasteful. Compile the graph with that checkpointer and store it in app.state.graph. Every endpoint then accesses the same compiled graph via app.state.graph. One connection, one graph, shared across all users and all requests for the entire server lifetime.
**Came up on:** 2026-05-14

### [Session 10] — Why compile the graph inside the lifespan context manager?
**Q:** Why is the graph compiled inside the lifespan async with block, not at module level?
**Status:** answered
**Answer:** The checkpointer (DB connection) only exists inside the `async with AsyncSqliteSaver` block. Compiling outside would mean no DB connection — no persistence. Lifespan runs once at server startup, opens the DB connection, compiles the graph, then `yield` — the server handles all requests here for hours/days/weeks. On shutdown, the `async with` block closes the connection cleanly. One connection, open for the lifetime of the server.
**Came up on:** 2026-05-14

### [Session 10] — What is app.state and why store the graph there?
**Q:** What is app.state.graph — where does .graph come from and why use app.state?
**Status:** answered
**Answer:** `app.state` is FastAPI's built-in shared storage — like a global variable safely attached to the app instance. `.graph` is a name you choose yourself: `app.state.graph = graph_builder.compile(...)`. Any endpoint that has `http_request.app.state` can read it. One compiled graph, shared across all endpoints, all users, all requests. You could name it anything — `app.state.myagent`, `app.state.whatever`. The name you store it under is the name you read it back with.
**Came up on:** 2026-05-14

### [Session 10] — Why SQLite for dev and Postgres for production?
**Q:** Can we share one open DB connection across multiple users?
**Status:** answered
**Answer:** Yes — one connection open for the server lifetime, shared across all requests. SQLite is fine for local dev (one write at a time limitation). In production use PostgreSQL + AsyncPostgresSaver — built for thousands of concurrent connections via connection pooling. A pool keeps say 10 connections open; requests borrow one, use it, return it. Same API as AsyncSqliteSaver, just swap the class and connection string.
**Came up on:** 2026-05-14

---

## Session 11 — LangSmith Observability

### [Session 11] — What does LangSmith actually give you?
**Q:** What can you do with LangSmith beyond just seeing if something failed?
**Status:** answered
**Answer:** Five use cases: (1) Debugging — agent gave wrong answer, trace shows exactly what the LLM received as input and what it returned, which node ran next, where it went wrong. (2) Cost tracking — tokens per run, which node is most expensive. (3) Latency — which node is slow, where the bottleneck is. (4) Regression testing — run agent against a test dataset before/after a prompt change, see if it actually improved. (5) User feedback — thumbs up/down attached to specific traces. Companies answer "we deployed a new prompt yesterday, did it actually help?" with LangSmith data. Zero code changes to the graph — just two env vars.
**Came up on:** 2026-05-14

---

## Session 12 — MCP with Real Tools

### [Session 12] — What changed from the fake MCP tool to the real one?
**Q:** What's structurally different between the fake search tool in Session 5.5 and the real Tavily tool?
**Status:** answered
**Answer:** Nothing structurally — same FastMCP, same @mcp.tool(), same mcp.run(transport="stdio"). Only what's inside the function changed: a real Tavily API call instead of a hardcoded string. The agent never knows or cares — it just sees a tool called "web_search" with a docstring. Could be fake, real, or a database query. That's the power of MCP — the agent is decoupled from what tools actually do.
**Came up on:** 2026-05-14

### [Session 12] — SSE vs MCP protocol vs HTTP — the layer confusion
**Q:** What is SSE, what is MCP protocol, and how do they relate to HTTP? Are they the same thing?
**Status:** answered
**Answer:** Three separate layers. HTTP = the transport, moves bytes between servers, same as any website. SSE (Server-Sent Events) = a feature of HTTP that keeps the connection open so the server can push multiple messages back without the client reconnecting — same thing used in /chat to stream tokens. MCP protocol = the language, structured messages that go over SSE: "here are my tools", "call this tool with these args", "here's the result". Stack: MCP protocol (meaning) → SSE (open connection) → HTTP (bytes). Same pattern as /chat: token chunks → SSE → HTTP. MCP just adds its own message format on top.
**Came up on:** 2026-05-14

### [Session 12] — stdio vs SSE in production
**Q:** In production, do you launch the MCP server as a subprocess on every request?
**Status:** answered
**Answer:** No — stdio launches a new subprocess every time, slow and wasteful. In production use SSE transport: MCP server runs as a separate long-running service exposed over HTTP. Agent connects to it via URL instead of launching a process. Only the outer transport layer changes — ClientSession stays identical. `stdio_client(server_params)` → `sse_client("https://your-mcp-server.com/sse")`. Two separately deployed services: FastAPI agent server + MCP tool server.
**Came up on:** 2026-05-14

### [Session 12] — How does MCP work in a multi-agent system with different tools per agent?
**Q:** If billing, research, and technical agents all need different tools, how does MCP help?
**Status:** answered
**Answer:** Two patterns. Pattern 1: one MCP server per domain — billing-tools-server for billing agent, research-tools-server for research agent. Different teams own different servers. Pattern 2: one MCP server with all tools, each agent selectively binds only what it needs. Companies start with Pattern 2, split into Pattern 1 as teams scale. Both patterns use the same ClientSession — only the server URL or tool filter changes.
**Came up on:** 2026-05-14

---

## Session 13 — Docker + Deployment

### [Session 13] — What problem does Docker solve?
**Q:** Why not just copy the code to a server and run it?
**Status:** answered
**Answer:** Without Docker: clone repo, install correct Python version, create venv, pip install all dependencies, set env vars, run uvicorn — one wrong Python version and it breaks. With Docker: one command `docker run`. The container has everything inside it — Python version, dependencies, code, config. Runs identically on your laptop, AWS, a colleague's machine. Three things Docker gives you: (1) Reproducibility — same behavior everywhere. (2) Isolation — app doesn't interfere with anything else on the server. (3) Deployability — every cloud provider knows how to run Docker containers.
**Came up on:** 2026-05-14

### [Session 13] — Dockerfile line by line
**Q:** What does each line in the Dockerfile do?
**Status:** answered
**Answer:** FROM python:3.11-slim = base image, official Python 3.11, slim = smaller size. WORKDIR /app = sets working directory inside container, all subsequent commands run from here. COPY requirements.txt . = copy deps file first (Docker caches this layer — if deps don't change, no reinstall). RUN pip install = install dependencies inside the container. COPY . . = copy all project code into the container. EXPOSE 8000 = open port 8000 so outside world can connect — without this the container is completely isolated. CMD uvicorn with --host 0.0.0.0 = listen on all network interfaces, not just localhost. Most common Docker mistake: forgetting 0.0.0.0 — app works locally, deployed in Docker, suddenly unreachable.
**Came up on:** 2026-05-14

### [Session 13] — Production Docker architecture for the full stack
**Q:** In production, how many containers do we need and what does each do?
**Status:** answered
**Answer:** Two containers minimum: (1) FastAPI agent container — runs session_10/main.py, handles /chat and /history endpoints, streams responses over SSE to frontend. (2) MCP tool server container — runs session_12/server.py with SSE transport, exposes /sse endpoint, agent connects to it over HTTP. Managed with docker-compose — defines both containers and how they communicate. In a real project: clean final_project/ folder, only production code, no session folders. One Dockerfile per container. Deploy both to cloud provider (Railway, Render, AWS).
**Came up on:** 2026-05-14

---

## Final Project — Phase 2 (Production Infrastructure)

### [Final Project] — Why switch from SQLite to PostgreSQL?
**Q:** What's wrong with SQLite in production?
**Status:** answered
**Answer:** SQLite is a file on disk — fine for local dev. In production with multiple containers or multiple server instances, every container would have its own separate SQLite file. Users would lose memory depending on which container their request hit. PostgreSQL is a separate service all containers connect to — one source of truth for all conversation history. Also handles concurrent writes (SQLite doesn't).
**Came up on:** 2026-05-16

### [Final Project] — Why switch from stdio to streamable-http for MCP?
**Q:** What's wrong with stdio MCP in production?
**Status:** answered
**Answer:** stdio launches a new subprocess every request — slow, wasteful, doesn't scale. streamable-http runs the MCP server as a separate long-lived container. FastAPI connects to it over HTTP at startup and keeps the connection open. Two independently scalable services. If you need more tool capacity, scale only the MCP container.
**Came up on:** 2026-05-16

### [Final Project] — DNS rebinding protection in FastMCP 1.27.1
**Q:** Why did FastMCP reject connections from the FastAPI container with 421 Misdirected Request?
**Status:** answered
**Answer:** FastMCP 1.27.1 added DNS rebinding protection — it checks the Host header of every incoming request against an allowlist. When FastAPI called `http://mcp-server:8080/mcp`, the Host header was `mcp-server:8080`, which wasn't in the allowlist. Fix: set `TransportSecuritySettings(allowed_hosts=["mcp-server:8080", "localhost:8080"])` in server.py before calling mcp.run(). In production you'd add your real domain instead.
**Came up on:** 2026-05-16

### [Final Project] — lifespan pattern in full production stack
**Q:** What is the pattern for the lifespan function when MCP + Postgres are both involved?
**Status:** answered
**Answer:** Open connections → build things with them → yield → app runs → connections close. In our case: open MCP connection → open ClientSession over it → open Postgres connection → build graph with those tools + checkpointer → store on app.state → yield. Everything is nested async with blocks because all connections must stay open for the server's entire lifetime. The moment you exit an async with block, that connection closes.
**Came up on:** 2026-05-16

### [Final Project] — Docker volumes mental model
**Q:** How do Docker volumes work and why does data survive container restarts?
**Status:** answered
**Answer:** Two sides to a volume mount: left side = the volume (where data actually lives, outside the container), right side = the path inside the container (how the container accesses it). Like plugging in a USB drive: the USB = the volume, the drive letter D:\ = the container path. Container restarts, dies, gets replaced — volume stays. New container attaches to the same volume, data is there. Works the same in Docker and Kubernetes. `docker compose down` keeps the volume. `docker compose down -v` deletes it.
**Came up on:** 2026-05-16

### [Final Project] — Tool execution loop pattern in specialist agents
**Q:** What is the pattern for an agent that can use tools?
**Status:** answered
**Answer:** Ask LLM → if it wants a tool, run it → feed result back → ask LLM again for final answer. Concretely: (1) llm.bind_tools(tools) at build time so LLM knows tools exist. (2) First ainvoke — LLM either answers or says "call web_search with this query". (3) If tool_calls: look up tool in tool_map by name, run it with LLM's args. (4) Build messages_with_result = original messages + AIMessage(tool_call) + ToolMessage(result). (5) Second ainvoke with full history → final answer. Without the AIMessage + ToolMessage in history, second LLM call wouldn't know a tool was called.
**Came up on:** 2026-05-16

### [Final Project] — Evaluation and guardrails in the context of LangGraph
**Q:** How do "evaluation" and "guardrails" (common JD terms) connect to what we built?
**Status:** answered
**Answer:** Evaluation = measuring if your agents are doing the right thing. Did the supervisor route correctly 95% of the time? Did the billing agent hallucinate a policy? Done with LangSmith evaluation + test datasets. Guardrails = stopping the agent from doing something it shouldn't. In LangGraph they're just conditional nodes or edges — a validation node that checks the message before routing further. Human-in-the-loop (Phase 3) is itself a manual guardrail. Companies hire for these because the LLM code is easy — making it reliable and safe in production is the hard part.
**Came up on:** 2026-05-16

### [Final Project] — Docker ports mental model
**Q:** Are container ports like 8000 (FastAPI) and 8080 (MCP) fixed?
**Status:** answered
**Answer:** Nothing is fixed — just conventions. FastAPI on 8000 because uvicorn docs use it, MCP on 8080 as "next available." You choose one port number and write it in two places inside the container: EXPOSE in Dockerfile + --port in CMD. Then map it in docker-compose ports section (right side must match what's inside, left side is whatever you want on your Mac). Rule: decide the container port, write it consistently inside the container, map it once in compose.
**Came up on:** 2026-05-16

### [Final Project] — Observability vs Evaluation — they are not the same thing
**Q:** When I set up LangSmith tracing, am I evaluating my agents?
**Status:** answered
**Answer:** No — tracing is observability, not evaluation. Observability = watching what happened (inputs, outputs, latency, tokens). Reactive — you look at it after something goes wrong. Evaluation = measuring if your agent is doing the right thing systematically. Proactive — you run it before deploying a change. To get evaluation in LangSmith you need: (1) a dataset of input/expected output pairs, (2) an evaluator function that scores outputs, (3) run evaluate() against the dataset. Most people set up tracing and think they're doing evaluation. They're not. They're just watching.
**Came up on:** 2026-05-16

### [Final Project] — How to evaluate a multi-agent system
**Q:** What do you evaluate first in a multi-agent system and what metrics do you get?
**Status:** answered
**Answer:** Start with the supervisor — it's the entry point. Dataset = input messages paired with expected next_agent values ("I need a refund" → "billing_agent"). Run them through the supervisor, check if next_agent matches expected, get a routing accuracy score. If routing accuracy is 90%, 1 in 10 customers gets sent to the wrong agent — real business problem. Then evaluate specialist agents: did billing agent answer correctly, did it hallucinate a policy? Supervisor routing is always eval step one because if routing is wrong, nothing downstream matters. Tools: LangSmith evaluate(), RAGAS (for RAG pipelines), or custom Python scripts.
**Came up on:** 2026-05-16

### [Final Project] — Evaluation datasets are different per agent
**Q:** Do you use the same input/output dataset for all agents?
**Status:** answered
**Answer:** No — each agent has a different job so each needs a different dataset and different metrics. Supervisor: input = user message, output = which agent was picked (routing accuracy, cheap to evaluate — just string matching). Billing agent: input = user message + billing context, output = response quality (did it hallucinate a policy?). Technical agent: input = error/issue, output = response + did it use web_search correctly. General agent: input = question, output = answer relevance. Prioritize eval budget on agents where mistakes are most expensive — wrong routing = annoying, wrong billing advice = potential lawsuit.
**Came up on:** 2026-05-16

### [Final Project] — Full evaluation process for production AI agents
**Q:** What is the right way to do evals as an AI engineer?
**Status:** answered
**Answer:** Three levels: (1) Unit evals — test each component in isolation: supervisor routing, tool selection, individual agent answer quality. (2) Integration evals — test full flow end to end: user message → correct agent → correct answer. (3) Production evals — real traffic, thumbs up/down from users, run evals on real conversations not just synthetic test cases. Three evaluator types: exact match (cheapest, for routing — just string compare), LLM as judge (for answer quality — ask an LLM to score 1-5), human review (most accurate, sample 10% of traffic). The process: write 20-30 test cases per agent before shipping → establish baseline → run same evals before every change → compare to baseline → monitor production in LangSmith → add new test cases when real users hit edge cases. Also evaluate MCP tool selection: did the agent call the right tool, did it NOT call a tool when it shouldn't have.
**Came up on:** 2026-05-16

### [Final Project] — Deployed MCP server to EC2, called from local FastAPI
**Q:** How do you deploy the MCP server to a real cloud machine and call it from a different machine?
**Status:** answered
**Answer:** Launch EC2 (t2.micro, Amazon Linux), install Docker + docker-compose, clone repo from GitHub, create .env on server, run `docker-compose up mcp-server --detach`. Open port 8080 in the security group. Update FastAPI to point at the EC2 public IP instead of `http://mcp-server:8080/mcp`. FastMCP DNS rebinding protection requires the EC2 IP to be in `allowed_hosts`. Architecture: local FastAPI → EC2 MCP server → Tavily. MCP server tools live on a different physical machine, FastAPI calls them over HTTP. This is the real production MCP pattern. `restart: always` in docker-compose keeps the container alive through reboots.
**Came up on:** 2026-05-18

### [Final Project] — Groq blocks certain IPs, switched to OpenAI gpt-4o-mini
**Q:** What to do when Groq returns 403 Access Denied?
**Status:** answered
**Answer:** Groq blocks certain ISP/network IPs with "Access denied. Please check your network settings." — not a key issue. Fix: switch to OpenAI. All 4 agents (supervisor, billing, technical, general) use `ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)`. Remove `base_url` — OpenAI doesn't need it. MCP server is unaffected since it only uses Tavily, not Groq.
**Came up on:** 2026-05-18

### [Final Project] — Never paste API keys in chat or public places
**Q:** What happens if you paste an API key publicly?
**Status:** answered
**Answer:** OpenAI and GitHub have automated secret scanners — they detect exposed keys within minutes and auto-revoke them. Always rotate a key immediately after accidental exposure. Store keys only in .env files that are in .gitignore. Never commit .env to git — GitHub push protection will block the push and force you to rewrite history with git filter-branch.
**Came up on:** 2026-05-18

### [Final Project] — Host header is the destination, not the source
**Q:** Why is the Host header the EC2 IP and not the local FastAPI IP?
**Status:** answered
**Answer:** The Host header is always the destination — where the request is going, not where it came from. When FastAPI on your Mac calls `http://52.23.195.78:8080/mcp`, the HTTP request includes `Host: 52.23.195.78:8080`. The MCP server reads that header and checks it against allowed_hosts. It doesn't care who sent the request — it cares where the request was addressed to. So allowed_hosts must contain the MCP server's own hostname/IP as seen by the caller.
**Came up on:** 2026-05-18

### [Final Project] — postgres hostname only works inside docker-compose network
**Q:** Why did we change the Postgres connection string from "postgres" to "localhost"?
**Status:** answered
**Answer:** "postgres" as a hostname only resolves inside Docker's internal network — Docker creates DNS entries for each service name. When FastAPI runs inside docker-compose it can reach Postgres via "postgres". When FastAPI runs directly on your Mac with uvicorn, there's no Docker network — "postgres" is an unknown hostname. But Postgres still has port 5432 mapped to your Mac, so "localhost:5432" works. Rule: inside docker-compose → use service name. Outside docker-compose → use localhost.
**Came up on:** 2026-05-18

### [Phase 3] — Human-in-the-loop full mental model
**Q:** How does human-in-the-loop actually work in production vs a script?
**Status:** answered
**Answer:** interrupt_after stops AFTER the agent runs (not before) — agent produces draft, graph pauses, human reviews. In a script you use input() to simulate approval. In production: (1) first invoke() runs agent, hits interrupt, FastAPI returns paused state to frontend. (2) Frontend shows "pending approval." (3) Human clicks Approve in a dashboard. (4) Click hits /approve/{thread_id} endpoint in FastAPI. (5) Endpoint calls invoke(None, config) — resumes graph. (6) Response goes to user. Graph waits in Postgres between pause and resume — could be seconds or hours. invoke(None, config) = resume with no new input. invoke({"messages": [...]}, config) = new message same thread, next conversation turn.
**Came up on:** 2026-05-18

### [Phase 3] — Workers, app.state, and why global variables fail in production
**Q:** Why does app.state work with multiple workers but global variables don't?
**Status:** answered
**Answer:** A worker is one running Python process. In production you run many: `uvicorn main:app --workers 4` = 4 separate processes, each with isolated memory. A global variable set in worker 1 doesn't exist in worker 2. app.state is also per-worker — BUT it works because the actual state (conversations, checkpoints) lives in Postgres, not the worker. Each worker builds an identical compiled graph in its own lifespan. They're identical so it doesn't matter which worker handles a request. 1000 users hitting 4 workers: each request gets the same graph structure from app.state, each gets their own conversation from Postgres via thread_id. One database, many identical workers. That's how it scales.
**Came up on:** 2026-05-18

### [Phase 3] — Human-in-the-loop built and working
**Q:** How does the /approve endpoint know the graph is paused and which thread to resume?
**Status:** answered
**Answer:** interrupt_after=["billing_agent"] in graph.compile() pauses the graph after billing agent runs. The paused state is saved to Postgres under the thread_id. /approve/{thread_id} loads app.state.graph, builds config with that thread_id, calls ainvoke(None, config) — None means no new input, just resume. LangGraph reads the checkpoint, finds where execution stopped, continues from there. The graph can wait in Postgres for seconds or days — doesn't matter. To enforce order (approve only after billing pauses), check state.next after /chat — if graph is still waiting, set status="pending_approval" in your own DB. /approve checks that status before resuming.
**Came up on:** 2026-05-19

### [Phase 3] — Who approves depends on the use case
**Q:** Who calls /approve — manager or user?
**Status:** answered
**Answer:** Whoever owns the decision. Refund approval = manager (user would always approve their own refund). Subscription cancellation confirmation = user ("are you sure?"). AI-drafted email review = user ("send this?"). The pattern is identical — whoever needs to approve calls /approve. The graph doesn't care who calls it, just that the endpoint is hit. In production this is wired to an internal dashboard, Slack bot, or confirmation UI depending on the use case.
**Came up on:** 2026-05-19

### [Phase 3] — Per-agent MCP servers: one Dockerfile, different command per service
**Q:** Do you need a separate Dockerfile for each MCP server?
**Status:** answered
**Answer:** No. One Dockerfile, no CMD line. docker-compose provides `command:` per service — that overrides whatever CMD the Dockerfile would have had. billing-mcp-server runs billing_server.py (port 8081), technical-mcp-server runs technical_server.py (port 8082), same image. Avoids duplicate Dockerfiles. Rule: Dockerfile = what's installed and copied. docker-compose command = what actually runs.
**Came up on:** 2026-05-19

### [Phase 3] — Per-agent MCP servers: lifespan opens two connections
**Q:** How does main.py handle two MCP servers instead of one?
**Status:** answered
**Answer:** Two nested `async with streamable_http_client(...)` blocks in lifespan. First opens billing MCP connection → gets billing_tools. Second opens technical MCP connection → gets technical_tools. Both stay open for the server lifetime. build_graph(billing_tools, technical_tools) receives them separately. billing_agent only gets billing_tools, technical_agent only gets technical_tools. Supervisor and general agents get no tools — they don't need them. On startup each MCP server logs "Processing request of type ListToolsRequest" — that's FastAPI discovering what tools each server exposes.
**Came up on:** 2026-05-19

### [Phase 3] — allowed_hosts must include Docker service name with port
**Q:** Why does allowed_hosts=["*"] not work but adding the service name does?
**Status:** answered
**Answer:** FastMCP's DNS rebinding protection does not treat "*" as a wildcard glob — it's a literal string match. The Host header sent by FastAPI is "billing-mcp-server:8081" (the Docker service name + port). That exact string must be in allowed_hosts. Fix: `allowed_hosts=["*", "billing-mcp-server:8081"]` — the literal service name and port. Same pattern for technical: `allowed_hosts=["*", "technical-mcp-server:8082"]`. Each time you add a new Docker service calling an MCP server, add its service-name:port to that server's allowed_hosts.
**Came up on:** 2026-05-19

---

## Open Questions (Unanswered)

*(none right now — all pre-session questions answered)*

---

## Things That Clicked Later

*(fill this in yourself when something suddenly makes sense)*

---
