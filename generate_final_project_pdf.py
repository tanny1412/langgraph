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
        "final_project/Final_Project_Plan.pdf",
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=26, textColor=colors.HexColor("#1a1a2e"), spaceAfter=6)

    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
        fontSize=13, textColor=colors.HexColor("#4a4a8a"),
        spaceAfter=20, alignment=TA_CENTER)

    h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
        fontSize=16, textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=20, spaceAfter=8)

    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#4a4a8a"),
        spaceBefore=14, spaceAfter=6)

    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, leading=16, textColor=colors.HexColor("#333333"),
        spaceAfter=6)

    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
        fontSize=10, leading=15, textColor=colors.HexColor("#333333"),
        leftIndent=16, spaceAfter=4, bulletIndent=6)

    code_style = ParagraphStyle("Code", parent=styles["Code"],
        fontSize=9, leading=14, textColor=colors.HexColor("#1a1a2e"),
        backColor=colors.HexColor("#f4f4f8"),
        leftIndent=12, rightIndent=12,
        spaceBefore=6, spaceAfter=6, borderPad=8)

    story = []

    # ── Cover ──────────────────────────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Final Project", title_style))
    story.append(Paragraph("Multi-Agent Customer Support System", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2,
                            color=colors.HexColor("#4a4a8a"), spaceAfter=16))
    story.append(Paragraph(
        "A production-ready customer support system built with LangGraph, FastAPI, MCP, "
        "LangSmith, and Docker. Three specialist agents, real web search tools, "
        "persistent memory, and a streaming REST API.",
        body_style))
    story.append(Spacer(1, 0.5*cm))

    # ── What It Does ──────────────────────────────────────────
    story.append(Paragraph("What It Does", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    flow = [
        "POST /chat  {message, thread_id}",
        "↓",
        "Supervisor Agent  →  reads message, routes to the right specialist",
        "↓",
        "Billing Agent      →  invoices, refunds, payments  (web search tool)",
        "Technical Agent    →  bugs, APIs, errors           (web search tool)",
        "General Agent      →  greetings, product info      (no tools)",
        "↓",
        "Streamed response back to user via SSE",
        "↓",
        "GET /history/{thread_id}  →  full conversation history",
    ]
    ft = Table([[row] for row in flow], colWidths=[14*cm])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f4f4f8")),
        ("FONTNAME", (0,0), (-1,-1), "Courier"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#1a1a2e")),
        ("PADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
    ]))
    story.append(ft)
    story.append(Spacer(1, 0.4*cm))

    # ── Architecture ──────────────────────────────────────────
    story.append(Paragraph("Full Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    arch = """\
Frontend (curl / React / mobile)
    ↓  HTTP
FastAPI Server  (final_project/api/main.py)
    ├── POST /chat          → streams response via SSE
    └── GET /history/{id}   → returns conversation history
        ↓
LangGraph Multi-Agent System  (final_project/graph.py)
    ├── Supervisor Agent    → routes based on message content
    ├── Billing Agent       → handles billing queries + web search
    ├── Technical Agent     → handles technical queries + web search
    └── General Agent       → handles everything else
        ↓  MCP over SSE (production) / stdio (dev)
MCP Tool Server  (final_project/mcp_server/server.py)
    └── web_search()        → Tavily real-time web search
        ↓
AsyncSqliteSaver            → conversation persistence
LangSmith                   → full observability (traces, costs, latency)
Docker                      → containerized, deployable anywhere"""

    story.append(Paragraph(arch.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(Spacer(1, 0.3*cm))

    # ── File Structure ────────────────────────────────────────
    story.append(Paragraph("File Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    structure = """\
final_project/
├── state.py                ← State TypedDict (shared across all agents)
├── graph.py                ← assembles the full multi-agent graph
├── agents/
│   ├── supervisor.py       ← reads message, returns next_agent
│   ├── billing.py          ← billing specialist + MCP web search
│   ├── technical.py        ← technical specialist + MCP web search
│   └── general.py          ← general assistant, no tools
├── mcp_server/
│   └── server.py           ← MCP server with Tavily web_search tool
├── api/
│   └── main.py             ← FastAPI app (lifespan, /chat, /history)
└── Dockerfile              ← containerizes the FastAPI server"""

    story.append(Paragraph(structure.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(Spacer(1, 0.4*cm))

    story.append(PageBreak())

    # ── Build Order ───────────────────────────────────────────
    story.append(Paragraph("Build Order", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    steps = [
        ("Step 1", "state.py",
         "Define the State TypedDict with messages (add_messages) and next_agent (str). "
         "This is the contract every agent reads and writes."),
        ("Step 2", "mcp_server/server.py",
         "Build the MCP tool server with a real Tavily web_search tool. "
         "Test it standalone before connecting to agents."),
        ("Step 3", "agents/supervisor.py",
         "Supervisor reads the user message and returns next_agent: "
         "'billing_agent', 'technical_agent', or 'general_agent'. "
         "Uses extraction loop + safe default."),
        ("Step 4", "agents/billing.py + technical.py + general.py",
         "Each specialist agent has its own system prompt and connects to the MCP server "
         "for web search. Billing and technical agents have tools. General does not."),
        ("Step 5", "graph.py",
         "Wire all nodes together: START → supervisor → conditional routing → "
         "specialist agent → END. Compile with AsyncSqliteSaver checkpointer."),
        ("Step 6", "api/main.py",
         "FastAPI server with lifespan (open DB + compile graph), "
         "POST /chat (streaming SSE), GET /history/{thread_id}."),
        ("Step 7", "Dockerfile",
         "Containerize the FastAPI server. Test with docker build + docker run. "
         "Verify /chat and /history work from inside the container."),
    ]

    for num, title, desc in steps:
        story.append(Paragraph(f"{num}: <b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 0.1*cm))

    story.append(Spacer(1, 0.4*cm))

    # ── Key Decisions ─────────────────────────────────────────
    story.append(Paragraph("Key Design Decisions", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    decisions = [
        ["Decision", "Choice", "Why"],
        ["Persistence", "AsyncSqliteSaver (dev) → PostgresSaver (prod)",
         "SQLite = zero setup. Swap one line for Postgres in production."],
        ["MCP transport", "stdio (dev) → SSE (prod)",
         "stdio = simple, no infra. SSE = separate container, scalable."],
        ["Streaming", "astream() + StreamingResponse + SSE",
         "Users see tokens as they arrive. Standard production pattern."],
        ["Supervisor routing", "Extraction loop + safe default",
         "LLMs don't follow exact format. Always validate, always have a fallback."],
        ["Observability", "LangSmith via env vars",
         "Zero code change. Captures every node, token, tool call automatically."],
        ["Containerization", "Docker with --host 0.0.0.0",
         "Runs identically anywhere. The most common Docker mistake avoided."],
    ]

    dt = Table(decisions, colWidths=[3.5*cm, 5*cm, 8*cm])
    dt.setStyle(TableStyle([
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
    story.append(dt)
    story.append(Spacer(1, 0.4*cm))

    # ── Build Phases ──────────────────────────────────────────
    story.append(Paragraph("Build Phases", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#ddddee"), spaceAfter=10))

    phases = [
        ("Phase 1 — Core System (runnable, interview-ready)", [
            "state.py — State TypedDict with messages + next_agent",
            "mcp_server/server.py — Tavily web_search tool over stdio",
            "agents/ — supervisor, billing, technical, general",
            "graph.py — full multi-agent graph with conditional routing",
            "api/main.py — FastAPI with /chat (SSE streaming) + /history",
            "AsyncSqliteSaver — conversation persistence",
            "LangSmith — observability via env vars",
            "Dockerfile — containerized FastAPI server",
        ]),
        ("Phase 2 — Production Infrastructure", [
            "Swap AsyncSqliteSaver → AsyncPostgresSaver",
            "Swap MCP stdio → SSE transport, MCP server as separate container",
            "docker-compose.yml — run FastAPI + MCP server together",
            "Deploy to Railway / Render / AWS — live URL",
        ]),
        ("Phase 3 — Advanced Patterns", [
            "Human-in-the-loop interrupt before billing agent sends refunds",
            "Auto-retry from checkpoint for failed agent runs",
            "Per-agent MCP tool servers (billing-tools-server, technical-tools-server)",
        ]),
    ]

    for phase_title, items in phases:
        story.append(Paragraph(phase_title, h2_style))
        for item in items:
            story.append(Paragraph(f"• {item}", bullet_style))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=2,
                            color=colors.HexColor("#4a4a8a"), spaceAfter=16))
    story.append(Paragraph(
        "This is not a tutorial project. This is the stack companies actually run.",
        ParagraphStyle("Rule", parent=body_style,
                       textColor=colors.HexColor("#4a4a8a"),
                       fontSize=11, borderPad=8,
                       backColor=colors.HexColor("#f0f0fa"))
    ))

    doc.build(story)
    print("PDF created: final_project/Final_Project_Plan.pdf")

if __name__ == "__main__":
    build_pdf()
