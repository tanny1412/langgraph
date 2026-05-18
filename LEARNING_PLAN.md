# LangGraph: From Zero to Production-Ready

## The Core Mental Model

```
LangChain  →  Linear chains (A → B → C → done)
LangGraph  →  Graphs with loops, branches, state (A → B → C → A again if needed)
```

Real company AI needs loops, decisions, and multiple agents working together.
LangGraph is how you build that.

---

## What We're Building (The Project)

A **Multi-Agent Research & Answer System** — the kind of thing companies actually deploy.

```
User Query
    ↓
[Router Agent]  →  decides what kind of question this is
    ↓
[Research Agent] or [Direct Answer Agent]
    ↓
[Critic Agent]  →  checks if the answer is good enough
    ↓ (loop back if not good enough)
[Final Output]
```

By the end, you'll have something that:
- Routes questions intelligently
- Does web research when needed
- Self-critiques and retries
- Remembers conversation history (persistence)
- Can pause for human approval (human-in-the-loop)
- Exposes a clean API (FastAPI integration)

---

## Phase 1 — Core Concepts (Sessions 1–3)

**Goal:** Understand the primitives. Build the smallest possible working graph.

### Session 1: State + Nodes
- What is State? (the shared memory of your graph)
- What is a Node? (a function that reads and updates state)
- Build: A graph with 2 nodes and a fixed edge. No LLM yet.

### Session 2: Edges + Conditional Routing
- Fixed edges vs conditional edges
- How the graph decides which node runs next
- Build: Add a router node that branches based on a keyword

### Session 3: Your First LLM Node
- Connecting an LLM (Claude/OpenAI) as a node
- How to inject LLM output into state
- Build: Replace the keyword router with an LLM-powered router

---

## Phase 2 — Real Patterns (Sessions 4–6)

**Goal:** Learn the patterns you'll use in 90% of company projects.

### Session 4: Loops + Termination Conditions
- How to loop in a graph (edge points back to an earlier node)
- How to decide when to stop looping
- Build: Add a critic node that loops back if quality is low

### Session 5: Tool Use inside a Graph
- Giving nodes access to tools (search, calculators, APIs)
- ReAct pattern (Reason + Act)
- Build: Add a research node that can call a web search tool

### Session 5.5: MCP — Model Context Protocol *(Bonus, between 5 and 6)*
- What MCP is and why companies use it (standardized tool access)
- How it differs from writing tools manually (discovery vs hardcoding)
- Running a local MCP server
- Connecting your LangGraph agent to an MCP server
- Build: Replace the manual search tool with an MCP-hosted tool. Same graph, different plumbing.

### Session 6: Multi-Agent Coordination
- Supervisor pattern (one agent delegates to others)
- How agents hand off state between each other
- Build: Supervisor that delegates to specialized sub-agents

---

## Phase 3 — Production Patterns (Sessions 7–9)

**Goal:** Make it something you'd actually deploy at a company.

### Session 7: Persistence & Memory
- Checkpointers (save graph state to a database)
- Multi-turn conversations (user can come back later)
- Build: Add SQLite persistence so conversations survive restarts

### Session 8: Human-in-the-Loop
- Interrupt points (graph pauses and waits for human input)
- Resume from where it paused
- Build: Add an approval step before final output goes to user

### Session 9: Streaming
- Stream tokens as they're generated (not wait for full response)
- Stream graph events (which node is running, what state looks like)
- Build: Add streaming output to the system

---

## Phase 4 — Production Stack (Sessions 10–13)

**Goal:** Build a real deployable system the way a company would ship it.

### Session 10: FastAPI Integration
- Expose the graph as async HTTP endpoints
- `POST /chat` — streaming SSE response with thread_id
- `POST /chat/resume` — resume after human-in-the-loop approval
- Async agent nodes with `astream()`
- Build: Full async FastAPI server wrapping the LangGraph agent

### Session 11: Observability & Debugging
- LangSmith tracing (see exactly what your graph did — every node, token, tool call)
- Trace failures, replay step-by-step, measure latency and token cost
- Build: Connect LangSmith to the FastAPI server — zero code change, just env vars

### Session 12: MCP Server with Real Tools
- Build a hosted MCP server with real tools (web search, file read, database query)
- Connect the multi-agent system to the MCP server
- Each specialist agent gets its own set of tools via MCP
- Build: Replace manual tools with MCP-hosted tools served from a dedicated server

### Session 13: Docker + Deployment
- Dockerize the full stack: FastAPI + LangGraph + MCP server
- Environment config and secrets management
- Deploy to a cloud provider (Railway / Render / AWS)
- Build: A running URL you can hand to anyone — portfolio-ready

---

## The Final Project Architecture

```
Frontend (or curl)
    ↓
FastAPI Server (session_10/)
    ├── POST /chat          → streams response via SSE
    ├── POST /chat/resume   → resumes after human approval
    └── GET /chat/history   → returns conversation history
        ↓
LangGraph Multi-Agent System
    ├── Supervisor Agent    → routes to specialist
    ├── Research Agent      → uses MCP tools
    ├── Billing Agent       → uses MCP tools
    └── Technical Agent     → uses MCP tools
        ↓
MCP Tool Server (session_12/)
    ├── web_search()
    ├── read_document()
    └── query_database()
        ↓
PostgreSQL (persistence)
LangSmith (observability)
Docker (deployment)
```

This is the stack companies actually run.

---

## Concepts Cheat Sheet

| Concept | What It Is | Analogy |
|---|---|---|
| State | Shared dict that all nodes read/write | A whiteboard in a room |
| Node | A function that takes state, returns updated state | A person doing a task |
| Edge | Connection between nodes | A handoff between people |
| Conditional Edge | Edge that picks the next node based on state | A manager deciding who to assign next |
| Checkpointer | Saves state to a DB at each step | Saving a video game |
| Interrupt | Graph pauses and waits | A workflow approval step |
| Supervisor | A node that routes to other agent-nodes | A project manager |

---

## Prerequisites

```bash
pip install langgraph langchain langchain-anthropic python-dotenv
```

You'll need:
- An Anthropic API key (or OpenAI)
- Python 3.11+
- Basic understanding of Python functions and dicts

---

## File Structure We'll Build Toward

```
LangGraph-basics/
├── LEARNING_PLAN.md         ← this file
├── .env                     ← API keys (never commit this)
├── session_01/
│   └── basic_graph.py       ← first graph, no LLM
├── session_02/
│   └── conditional_graph.py ← branching
├── session_03/
│   └── llm_graph.py         ← first LLM node
├── ...
└── final_project/
    ├── agents/
    ├── tools/
    ├── api/
    └── main.py
```

Each session folder is self-contained. You can always go back.

---

## Final Project — Phase 3 (After Deployment)

### Session: Agent Evaluation
Build a proper evaluation pipeline for the customer support system.

**What we'll build:**
- 25-case dataset for the supervisor (input message → expected next_agent)
- Exact match evaluator for routing accuracy
- LLM-as-judge evaluator for specialist agent answer quality
- Tool selection eval (did agent call the right tool, or no tool?)
- Run everything with LangSmith evaluate() and get a real accuracy score
- Change the supervisor prompt, rerun evals, see if score improves

**Why it matters:** Evaluation is the difference between hoping your agent works and knowing it does. Routing accuracy, answer quality, tool selection — each agent needs its own dataset and its own metric. Baseline → change → rerun → ship or revert. This is the cycle that separates teams that improve their agents from teams that just hope.

**Eval levels to cover:**
1. Unit evals — supervisor routing, tool selection, individual agent answer quality
2. Integration evals — full flow end to end
3. Production evals — real traffic, thumbs up/down from users in LangSmith

---

## Future Work — Advanced Patterns (Post Session 12)

These are production-grade concepts that came up during learning but are beyond the 12-session scope. Build these after the core plan is complete.

### Auto-Retry from Checkpoint
When an agent fails mid-workflow, automatically roll back to the last good checkpoint and retry — without restarting from zero.

Key APIs:
- `graph_app.get_state_history(config)` — returns all checkpoints for a thread, newest first
- `graph_app.invoke(None, retry_config)` — resume from a specific checkpoint_id (None = no new input)

Pattern:
```python
def invoke_with_retry(graph_app, input, config):
    try:
        return graph_app.invoke(input, config)
    except Exception:
        checkpoints = list(graph_app.get_state_history(config))
        last_good = checkpoints[1]  # 0 = failed, 1 = last good
        retry_config = {
            "configurable": {
                "thread_id": config["configurable"]["thread_id"],
                "checkpoint_id": last_good.config["configurable"]["checkpoint_id"]
            }
        }
        return graph_app.invoke(None, retry_config)
```

Why it matters: long-running workflows (10+ steps) shouldn't restart from zero on failure. This is the production-grade resilience pattern.

Prerequisite: Session 7 (persistence) + Session 11 (LangSmith to detect which step failed)

---

## The Rule We Follow

> Never skip steps. Every session must run and produce visible output before we move on.

We build like a company would: get it working, understand it, then extend it.
