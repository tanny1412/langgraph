# LangGraph Learning Project — CLAUDE.md

## Who I Am
Tanish — strong Python, good LLM fundamentals, understands LangChain conceptually but hasn't integrated it deeply. Has Claude + OpenAI keys. Starting work soon so there's real urgency.

## Goal
Learn LangGraph the company way — not just tutorials. Build something real that can be shown to an employer or used as a template on the job.

## Teaching Rules (Non-Negotiable)
- Never one-shot the full solution. Build one function or concept at a time.
- Every step must run and produce visible output before moving forward.
- Always explain the WHY before the HOW.
- If I ask "what does X do", explain it relative to what I already know (Python + LLMs).
- When introducing a new concept, show the simplest possible version first. Complexity comes later.

## Project We're Building
A Multi-Agent Research & Answer System across 12 sessions.
Plan lives in: `LEARNING_PLAN.md`
Full PDF plan: `LangGraph_Project_Plan.pdf`

## Session Structure
Each session lives in its own folder: `session_01/`, `session_02/`, etc.
Each folder has one focused Python file. No mixing concerns across sessions.

## Code Style for This Project
- No unnecessary comments — variable names should explain themselves
- Type hints on all function signatures
- Never use `Any` type — be explicit
- State classes use TypedDict (LangGraph standard)
- Keep nodes as plain functions — no classes unless the complexity demands it

## API Keys
- Anthropic key: in `.env` as `ANTHROPIC_API_KEY`
- OpenAI key: in `.env` as `OPENAI_API_KEY`
- Tavily key (get when we reach Session 5): `TAVILY_API_KEY`
- Never commit `.env`

## MCP (Model Context Protocol)
MCP is how companies standardize tool access at scale. Instead of writing custom tool functions
for every system, you connect an MCP server and the agent discovers tools automatically.
We cover it in Session 5.5 (bonus session between 5 and 6) — after you understand tools manually.

MCP servers we'll build:
- A local filesystem MCP server (read/write files as a tool)
- Connecting to an external MCP server (e.g., a database)
- How LangGraph agents discover and use MCP tools

## Where We Are
- [x] Learning plan created
- [x] PDF plan generated: LangGraph_Project_Plan.pdf
- [x] Session 1: State + Nodes — complete (session_01/basic_graph.py)
- [x] Session 2: Edges + Conditional Routing — complete (session_02/conditional_graph.py)
- [x] Session 3: LLM Router — complete (session_03/llm_router.py) — using Groq free tier
- [x] Session 4: Loops + Termination — complete (session_04/loop_graph.py)
- [x] Session 5: Tool Use — complete (session_05/tool_agent.py) — Groq llama-3.3-70b-versatile
- [x] Session 5.5: MCP — complete (session_05_mcp/server.py + agent.py)
- [x] Session 6: Multi-Agent Coordination — complete (session_06/multi_agent.py)
- [ ] Session 7: Persistence & Memory (start here)

## LangChain vs LangGraph — The One-Line Reminder
LangChain = linear pipeline. LangGraph = graph with state, loops, branches, multiple agents.
