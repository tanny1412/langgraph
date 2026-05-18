from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

def build_pdf():
    doc = SimpleDocTemplate(
        "LangGraph_Project_Plan.pdf",
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=26, textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6)

    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
        fontSize=13, textColor=colors.HexColor("#4a4a8a"),
        spaceAfter=20, alignment=TA_CENTER)

    h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
        fontSize=16, textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=20, spaceAfter=8,
        borderPad=4)

    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#4a4a8a"),
        spaceBefore=14, spaceAfter=6)

    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, leading=16, textColor=colors.HexColor("#333333"),
        spaceAfter=6)

    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
        fontSize=10, leading=15, textColor=colors.HexColor("#333333"),
        leftIndent=16, spaceAfter=4,
        bulletIndent=6)

    code_style = ParagraphStyle("Code", parent=styles["Code"],
        fontSize=9, leading=14, textColor=colors.HexColor("#1a1a2e"),
        backColor=colors.HexColor("#f4f4f8"),
        leftIndent=12, rightIndent=12,
        spaceBefore=6, spaceAfter=6,
        borderPad=8)

    tag_style = ParagraphStyle("Tag", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#ffffff"),
        backColor=colors.HexColor("#4a4a8a"),
        alignment=TA_CENTER)

    story = []

    # ── Cover ──────────────────────────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("LangGraph", title_style))
    story.append(Paragraph("From Zero to Production-Ready", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2,
                            color=colors.HexColor("#4a4a8a"), spaceAfter=16))
    story.append(Paragraph(
        "A 13-session mentor-led learning path for Tanish — "
        "built to get you company-ready, not just tutorial-ready.",
        body_style))
    story.append(Spacer(1, 0.5*cm))

    # ── The Core Mental Model ──────────────────────────────────
    story.append(Paragraph("The Core Mental Model", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    story.append(Paragraph(
        "LangChain gives you a <b>linear pipeline</b>: A → B → C → done. "
        "That covers maybe 20% of what companies actually need.", body_style))
    story.append(Paragraph(
        "LangGraph gives you a <b>graph</b>: nodes that do work, edges that connect them, "
        "and state that flows through everything. This unlocks loops, branches, "
        "multiple agents, and human approval steps.", body_style))

    table_data = [
        ["Concept", "LangChain", "LangGraph"],
        ["Execution", "Linear only", "Graph — loops + branches"],
        ["State", "Passed manually", "Shared TypedDict, auto-managed"],
        ["Agents", "Single chain", "Multiple agents, supervisor pattern"],
        ["Memory", "Manual", "Built-in checkpointers"],
        ["Human-in-loop", "Hacky", "First-class interrupt points"],
    ]
    t = Table(table_data, colWidths=[4.5*cm, 6*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#f4f4f8"), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # ── What We're Building ────────────────────────────────────
    story.append(Paragraph("What We're Building", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))
    story.append(Paragraph(
        "A <b>Multi-Agent Research &amp; Answer System</b> — the kind of thing "
        "companies actually deploy for internal tools, customer support, and knowledge bases.",
        body_style))

    flow_data = [
        ["User Query"],
        ["↓"],
        ["Router Agent  →  decides what kind of question this is"],
        ["↓"],
        ["Research Agent  OR  Direct Answer Agent"],
        ["↓"],
        ["Critic Agent  →  checks quality, loops back if not good enough"],
        ["↓"],
        ["Human Approval (optional)  →  interrupt point"],
        ["↓"],
        ["Final Output  →  streamed via FastAPI"],
    ]
    ft = Table([[row[0]] for row in flow_data], colWidths=[14*cm])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f4f4f8")),
        ("FONTNAME", (0,0), (-1,-1), "Courier"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#1a1a2e")),
        ("PADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
    ]))
    story.append(ft)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("By the end you will have:", body_style))
    bullets = [
        "A working multi-agent system you can demo to an employer",
        "Understood every core LangGraph primitive from first principles",
        "Patterns for routing, looping, tool use, and agent coordination",
        "Persistence (conversation memory that survives restarts)",
        "A REST API wrapper — the way companies actually expose AI systems",
        "A hosted MCP server with real tools connected to your agents",
        "Observability via LangSmith tracing",
        "A Dockerized deployable system — docker run and it works anywhere",
    ]
    for b in bullets:
        story.append(Paragraph(f"• {b}", bullet_style))

    story.append(PageBreak())

    # ── Sessions ──────────────────────────────────────────────
    phases = [
        {
            "phase": "Phase 1 — Core Concepts  (Sessions 1–3)",
            "goal": "Understand the primitives. Build the smallest possible working graph before touching an LLM.",
            "sessions": [
                {
                    "num": "Session 1",
                    "title": "State + Nodes",
                    "concepts": ["TypedDict State — the shared whiteboard",
                                 "Nodes — plain Python functions that read and update state",
                                 "StateGraph — how you wire nodes together",
                                 "compile() + invoke() — running your first graph"],
                    "build": "A 2-node graph with no LLM. Input goes in, transformed output comes out. You'll see the state change at each step.",
                    "why": "You need to understand the container (graph + state) before you put anything smart inside it."
                },
                {
                    "num": "Session 2",
                    "title": "Edges + Conditional Routing",
                    "concepts": ["Fixed edges vs conditional edges",
                                 "add_conditional_edges() — how the graph decides what runs next",
                                 "END — how a graph knows it's done",
                                 "Visualizing your graph"],
                    "build": "Add a router node that sends the flow to one of two different processing nodes based on a keyword in the input.",
                    "why": "Branching is what separates a graph from a chain. This is the session where LangGraph starts to feel different."
                },
                {
                    "num": "Session 3",
                    "title": "Your First LLM Node",
                    "concepts": ["ChatAnthropic inside a node",
                                 "Messages state pattern (HumanMessage, AIMessage)",
                                 "LLM-powered routing (not just keyword matching)",
                                 "Keeping nodes stateless — why this matters"],
                    "build": "Replace the keyword router with an LLM that reads the query and decides the route. Same graph structure, smarter decision-making.",
                    "why": "This is the moment the graph becomes an AI system. Everything before this was scaffolding."
                },
            ]
        },
        {
            "phase": "Phase 2 — Real Patterns  (Sessions 4–6)",
            "goal": "The patterns you'll use in 90% of company AI projects.",
            "sessions": [
                {
                    "num": "Session 4",
                    "title": "Loops + Termination",
                    "concepts": ["Pointing an edge back to an earlier node",
                                 "Termination conditions (max retries, quality threshold)",
                                 "Tracking loop count in state",
                                 "Why infinite loops are a real risk and how to prevent them"],
                    "build": "Add a Critic node that reads the output, scores it, and loops back to regenerate if the score is too low. Stops after 3 attempts.",
                    "why": "Self-correction loops are one of the most common patterns in production AI. This is how you build reliability."
                },
                {
                    "num": "Session 5",
                    "title": "Tool Use inside a Graph",
                    "concepts": ["Defining tools as decorated functions",
                                 "ToolNode — the LangGraph built-in for executing tools",
                                 "ReAct pattern: Reason → Act → Observe → Repeat",
                                 "Tavily web search tool (get your free key here)"],
                    "build": "Add a Research node that can call a web search tool. The LLM decides when to search and what to search for.",
                    "why": "Tools are how agents interact with the real world. This session connects your graph to live information."
                },
                {
                    "num": "Session 6",
                    "title": "Multi-Agent Coordination",
                    "concepts": ["Supervisor pattern — one agent delegates to others",
                                 "Subgraphs — graphs inside graphs",
                                 "Agent handoff via state",
                                 "When to use one agent vs many"],
                    "build": "A Supervisor agent that reads the query and delegates to either a Research Agent or a Direct Answer Agent. Each is its own subgraph.",
                    "why": "This is the architecture pattern most companies use. You're now building the thing, not a toy."
                },
            ]
        },
        {
            "phase": "Phase 3 — Production Patterns  (Sessions 7–9)",
            "goal": "Make it something you'd actually deploy. This is what separates tutorial engineers from company engineers.",
            "sessions": [
                {
                    "num": "Session 7",
                    "title": "Persistence & Memory",
                    "concepts": ["Checkpointers — saving graph state after every step",
                                 "SQLite checkpointer (local) vs Postgres (production)",
                                 "thread_id — how multi-turn conversations work",
                                 "Resuming a conversation from where it left off"],
                    "build": "Add SQLite persistence. Stop the program, restart it, pick up the conversation exactly where you left off.",
                    "why": "Without persistence your agent forgets everything on restart. No real product ships without this."
                },
                {
                    "num": "Session 8",
                    "title": "Human-in-the-Loop",
                    "concepts": ["interrupt() — pausing a graph mid-execution",
                                 "Command(resume=...) — sending input back into a paused graph",
                                 "Where to put interrupt points (before risky actions)",
                                 "Combining interrupts with persistence"],
                    "build": "Add an approval step before the final answer is sent. The graph pauses, you (as human) review the draft, then resume or reject.",
                    "why": "Every enterprise AI system has human oversight somewhere. This is how you build it properly."
                },
                {
                    "num": "Session 9",
                    "title": "Streaming",
                    "concepts": ["stream() vs invoke() — the difference",
                                 "Streaming tokens as they generate (not waiting for full response)",
                                 "Streaming graph events (which node is active, state snapshots)",
                                 "astream() for async contexts"],
                    "build": "Replace invoke() with stream() throughout. Output appears token-by-token like ChatGPT.",
                    "why": "Users hate waiting. Streaming is a UX requirement, not a nice-to-have."
                },
            ]
        },
        {
            "phase": "Phase 4 — Production Stack  (Sessions 10–13)",
            "goal": "Build a real deployable system the way a company ships it. This is the gap most engineers never close.",
            "sessions": [
                {
                    "num": "Session 10",
                    "title": "FastAPI Integration",
                    "concepts": ["Async LangGraph with FastAPI",
                                 "POST /chat — streaming SSE response with thread_id",
                                 "POST /chat/resume — resume after human-in-the-loop approval",
                                 "Async agent nodes with astream()"],
                    "build": "A full async FastAPI server wrapping the LangGraph agent. curl a question, get a streamed answer. Hit /resume to approve a paused graph.",
                    "why": "LangGraph code lives on a server. FastAPI is how the rest of the company talks to it — and how users actually experience it."
                },
                {
                    "num": "Session 11",
                    "title": "Observability with LangSmith",
                    "concepts": ["LangSmith — tracing every node, token, and tool call automatically",
                                 "Reading traces to debug wrong outputs step by step",
                                 "Adding metadata to traces (user_id, session_id)",
                                 "Cost tracking and latency per run"],
                    "build": "Connect LangSmith to the FastAPI server — zero code change, just env vars. Run a query, inspect the full execution trace in the dashboard.",
                    "why": "You cannot debug a production AI system without traces. This is the first thing any company will ask about."
                },
                {
                    "num": "Session 12",
                    "title": "MCP Server with Real Tools",
                    "concepts": ["Build a hosted MCP server with real tools (web search, file read, DB query)",
                                 "Connect the multi-agent system to the hosted MCP server",
                                 "Each specialist agent gets its own set of MCP tools",
                                 "Swap manual tools for MCP-hosted tools — zero agent code change"],
                    "build": "A running MCP tool server. Billing agent connects to billing tools, research agent connects to search tools. All served from one MCP server.",
                    "why": "This is how companies standardize tool access at scale. One team maintains the tools, every agent just connects."
                },
                {
                    "num": "Session 13",
                    "title": "Docker + Deployment",
                    "concepts": ["Dockerfile — FROM, WORKDIR, COPY, RUN, EXPOSE, CMD",
                                 "--host 0.0.0.0 — the most common Docker mistake to avoid",
                                 "docker-compose for multi-container setup (agent + MCP server)",
                                 "Deploy to Railway / Render / AWS — a live URL you can hand to anyone"],
                    "build": "docker build + docker run. FastAPI agent runs in a container, responds to HTTP requests. Full stack containerized and ready to deploy.",
                    "why": "Code that only runs on your laptop isn't shipped. This session closes the loop."
                },
            ]
        },
    ]

    for phase in phases:
        story.append(Paragraph(phase["phase"], h1_style))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#ddddee"), spaceAfter=8))
        story.append(Paragraph(f"<i>Goal: {phase['goal']}</i>", body_style))
        story.append(Spacer(1, 0.2*cm))

        for s in phase["sessions"]:
            story.append(Paragraph(f"{s['num']}: {s['title']}", h2_style))
            story.append(Paragraph("<b>Concepts:</b>", body_style))
            for c in s["concepts"]:
                story.append(Paragraph(f"• {c}", bullet_style))
            story.append(Paragraph(f"<b>What you'll build:</b> {s['build']}", body_style))
            story.append(Paragraph(f"<b>Why this session matters:</b> {s['why']}", body_style))
            story.append(Spacer(1, 0.2*cm))

        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # ── Concepts Cheat Sheet ──────────────────────────────────
    story.append(Paragraph("Concepts Cheat Sheet", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    cheat = [
        ["Concept", "What It Is", "Real-World Analogy"],
        ["State", "Shared TypedDict that all nodes read/write", "A whiteboard in a meeting room"],
        ["Node", "A function: takes state, returns updated state", "A person doing one specific task"],
        ["Edge", "Connection between two nodes", "Handing work to the next person"],
        ["Conditional Edge", "Picks next node based on state value", "A manager deciding who to assign next"],
        ["Checkpointer", "Saves state to a DB after every step", "Saving a video game mid-level"],
        ["interrupt()", "Pauses the graph and waits for human input", "A workflow approval step"],
        ["Supervisor", "A node that routes to other agent-nodes", "A project manager delegating tasks"],
        ["Subgraph", "A full graph used as a single node", "A team that handles a whole workstream"],
        ["ToolNode", "Built-in node that executes tool calls from LLM", "An assistant who can Google things"],
    ]
    ct = Table(cheat, colWidths=[3.5*cm, 6.5*cm, 6.5*cm])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#f4f4f8"), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.6*cm))

    # ── File Structure ────────────────────────────────────────
    story.append(Paragraph("Project File Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    structure = """\
LangGraph-basics/
├── CLAUDE.md                ← project rules and context for Claude Code
├── LEARNING_PLAN.md         ← this plan in markdown
├── LangGraph_Project_Plan.pdf
├── .env                     ← API keys (never commit)
├── session_01/
│   └── basic_graph.py
├── session_02/
│   └── conditional_graph.py
├── ...
├── session_12/
│   └── mcp_tools/
├── session_13/
│   └── deployment/
└── final_project/
    ├── agents/
    │   ├── router.py
    │   ├── researcher.py
    │   ├── critic.py
    │   └── supervisor.py
    ├── mcp_server/
    │   ├── server.py        ← hosted MCP tool server
    │   └── tools/
    ├── api/
    │   └── main.py          ← FastAPI app
    ├── graph.py             ← assembled full graph
    └── Dockerfile"""

    story.append(Paragraph(structure.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    # ── Setup ─────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Setup Before Session 1", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    setup = "pip install langgraph langchain langchain-anthropic langchain-openai python-dotenv"
    story.append(Paragraph(setup, code_style))

    story.append(Paragraph("Create a <b>.env</b> file in the project root:", body_style))
    env_content = "ANTHROPIC_API_KEY=your_key_here\nOPENAI_API_KEY=your_key_here"
    story.append(Paragraph(env_content.replace("\n", "<br/>"), code_style))

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "The single rule that matters most: <b>every session ends with running code. "
        "If it doesn't run, we don't move on.</b>",
        ParagraphStyle("Rule", parent=body_style,
                       textColor=colors.HexColor("#4a4a8a"),
                       fontSize=11, borderPad=8,
                       backColor=colors.HexColor("#f0f0fa"))
    ))

    doc.build(story)
    print("PDF created: LangGraph_Project_Plan.pdf")

if __name__ == "__main__":
    build_pdf()
