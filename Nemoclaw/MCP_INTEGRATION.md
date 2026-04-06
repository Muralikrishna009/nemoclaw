# Connecting OpenClaw (NemoClaw) to the MCP Server

## How It Works

```
User (Telegram)
      │
      ▼
OpenClaw Bot (EC2)
      │  1. User asks: "Generate Q1 financial report"
      │  2. Bot checks user's RBAC permissions
      │  3. Bot calls MCP tool endpoint
      │  4. MCP returns file_url
      │  5. Bot sends file back to user
      ▼
MCP Server (http://localhost:8000)
```

---

## 1. Environment Variable in OpenClaw

Add to your OpenClaw `.env`:
```env
MCP_SERVER_URL=http://localhost:8000
ADMIN_PANEL_URL=http://localhost:3000
```

If MCP and OpenClaw are on **different machines**, use the private EC2 IP:
```env
MCP_SERVER_URL=http://<EC2-PRIVATE-IP>:8000
```

---

## 2. MCP Client Module

Create this file in your OpenClaw project:

```python
# mcp_client.py

import httpx
from typing import Optional

MCP_SERVER_URL = "http://localhost:8000"
ADMIN_PANEL_URL = "http://localhost:3000"


# ── RBAC Check ────────────────────────────────────────────────────────────────

async def get_user_permissions(telegram_id: str) -> dict:
    """
    Fetch user info + permissions from the admin panel API.
    Returns: { "allowed": bool, "permissions": [...], "user": {...} }
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{ADMIN_PANEL_URL}/api/users")
        users = res.json()

    user = next((u for u in users if u.get("telegramId") == str(telegram_id)), None)

    if not user:
        return {"allowed": False, "reason": "User not registered", "permissions": []}

    if not user.get("isActive"):
        return {"allowed": False, "reason": "Your account is inactive. Contact admin.", "permissions": []}

    permissions = [
        rp["permission"]["name"]
        for rp in user["role"]["rolePermissions"]
    ]

    return {"allowed": True, "permissions": permissions, "user": user}


async def can_use_tool(telegram_id: str, tool: str) -> tuple[bool, str]:
    """
    Check if user can use a specific tool.
    Returns: (allowed: bool, reason: str)
    """
    result = await get_user_permissions(telegram_id)
    if not result["allowed"]:
        return False, result["reason"]
    if tool not in result["permissions"]:
        return False, f"You don't have permission to use `{tool}`."
    return True, "ok"


# ── MCP Tool Calls ────────────────────────────────────────────────────────────

async def generate_pdf(
    report_type: str = "financial",
    title: str = None,
    period: str = "Q1 2025",
    department: str = None,
) -> dict:
    """
    Call MCP to generate a PDF report.
    Returns: { "success": bool, "file_url": str, "file_path": str }
    """
    payload = {
        "report_type": report_type,
        "title": title or f"{report_type.title()} Report",
        "params": {"period": period},
    }
    if department:
        payload["params"]["department"] = department

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(f"{MCP_SERVER_URL}/tools/generate-pdf", json=payload)
        res.raise_for_status()
        return res.json()


async def generate_image(
    diagram_type: str = "flowchart",
    title: str = None,
    flow: str = "order_processing",
    period: str = "Q1 2025",
    nodes: list = None,
    edges: list = None,
) -> dict:
    """
    Call MCP to generate a diagram or chart.
    Returns: { "success": bool, "file_url": str, "file_path": str }
    """
    payload = {
        "diagram_type": diagram_type,
        "title": title or diagram_type.replace("_", " ").title(),
        "params": {"flow": flow, "period": period},
    }
    if nodes:
        payload["nodes"] = nodes
    if edges:
        payload["edges"] = edges

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(f"{MCP_SERVER_URL}/tools/generate-image", json=payload)
        res.raise_for_status()
        return res.json()


async def download_file(file_url: str) -> bytes:
    """Download a generated file as bytes (to send via Telegram)."""
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(f"{MCP_SERVER_URL}{file_url}")
        res.raise_for_status()
        return res.content
```

---

## 3. Wiring Into OpenClaw Bot Handlers

```python
# In your bot handler (python-telegram-bot / aiogram / etc.)

from mcp_client import can_use_tool, generate_pdf, generate_image, download_file
import io


# ── PDF Handler ───────────────────────────────────────────────────────────────

async def handle_generate_pdf(update, context):
    telegram_id = str(update.effective_user.id)

    # 1. RBAC check
    allowed, reason = await can_use_tool(telegram_id, "generate_pdf")
    if not allowed:
        await update.message.reply_text(f"Access denied: {reason}")
        return

    # 2. Parse what the user asked (simple keyword matching — replace with your LLM logic)
    text = update.message.text.lower()
    report_type = "financial"
    if "summary" in text:
        report_type = "summary"
    elif "invoice" in text:
        report_type = "invoice"

    period = "Q1 2025"
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        if q.lower() in text:
            year = "2025"
            period = f"{q} {year}"
            break

    await update.message.reply_text("Generating your report...")

    # 3. Call MCP
    result = await generate_pdf(report_type=report_type, period=period)

    # 4. Download and send file
    file_bytes = await download_file(result["file_url"])
    await update.message.reply_document(
        document=io.BytesIO(file_bytes),
        filename=f"{report_type}_report.pdf",
        caption=f"{report_type.title()} Report — {period}",
    )


# ── Image Handler ─────────────────────────────────────────────────────────────

async def handle_generate_image(update, context):
    telegram_id = str(update.effective_user.id)

    allowed, reason = await can_use_tool(telegram_id, "generate_image")
    if not allowed:
        await update.message.reply_text(f"Access denied: {reason}")
        return

    text = update.message.text.lower()
    diagram_type = "flowchart"
    if "chart" in text or "bar" in text:
        diagram_type = "bar_chart"
    elif "org" in text:
        diagram_type = "org_chart"

    flow = "order_processing"
    if "onboard" in text:
        flow = "onboarding"
    elif "support" in text or "ticket" in text:
        flow = "support_ticket"

    await update.message.reply_text("Generating diagram...")

    result = await generate_image(diagram_type=diagram_type, flow=flow)

    file_bytes = await download_file(result["file_url"])
    await update.message.reply_photo(
        photo=io.BytesIO(file_bytes),
        caption=result["message"],
    )
```

---

## 4. LLM-Driven Tool Calling (Recommended)

If OpenClaw uses an LLM to decide which tool to call, structure it like this:

```python
# tools_schema.py — pass this to your LLM as available tools

TOOLS = [
    {
        "name": "generate_pdf",
        "description": "Generate a PDF financial report. Use when user asks for reports, financials, invoices, summaries.",
        "parameters": {
            "report_type": "financial | summary | invoice",
            "title": "string (optional)",
            "period": "Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025",
            "department": "Sales | Engineering | Marketing | Operations | HR (optional)",
        },
    },
    {
        "name": "generate_image",
        "description": "Generate a diagram or chart. Use when user asks for flowcharts, org charts, bar charts, diagrams.",
        "parameters": {
            "diagram_type": "flowchart | org_chart | bar_chart",
            "title": "string (optional)",
            "flow": "order_processing | onboarding | support_ticket (for flowchart)",
            "period": "Q1 2025 | Q2 2025 | ... (for bar_chart)",
        },
    },
]
```

```python
# In your LLM handler

async def handle_message(update, context):
    telegram_id = str(update.effective_user.id)
    user_message = update.message.text

    # 1. Ask LLM which tool to use (pseudo-code — adapt to your LLM setup)
    llm_response = await your_llm.call(
        system="You are NemoClaw. Decide if the user needs generate_pdf or generate_image. Extract parameters.",
        tools=TOOLS,
        message=user_message,
    )

    if llm_response.tool == "generate_pdf":
        allowed, reason = await can_use_tool(telegram_id, "generate_pdf")
        if not allowed:
            await update.message.reply_text(reason)
            return
        result = await generate_pdf(**llm_response.tool_params)
        file_bytes = await download_file(result["file_url"])
        await update.message.reply_document(io.BytesIO(file_bytes), filename="report.pdf")

    elif llm_response.tool == "generate_image":
        allowed, reason = await can_use_tool(telegram_id, "generate_image")
        if not allowed:
            await update.message.reply_text(reason)
            return
        result = await generate_image(**llm_response.tool_params)
        file_bytes = await download_file(result["file_url"])
        await update.message.reply_photo(io.BytesIO(file_bytes))

    else:
        # Normal LLM reply — no tool needed
        await update.message.reply_text(llm_response.text)
```

---

## 5. Add httpx to OpenClaw

```bash
pip install httpx
```

---

## 6. Verify Connection

From the OpenClaw server, test MCP is reachable:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/tools
```

---

## 7. Example Conversations

| User says | Tool called | Params |
|-----------|------------|--------|
| "Generate Q2 financial report" | `generate_pdf` | `report_type=financial, period=Q2 2025` |
| "Show me the invoice list" | `generate_pdf` | `report_type=invoice` |
| "Draw the order processing flow" | `generate_image` | `diagram_type=flowchart, flow=order_processing` |
| "Show me a bar chart for Q3" | `generate_image` | `diagram_type=bar_chart, period=Q3 2025` |
| "Show company org chart" | `generate_image` | `diagram_type=org_chart` |
| "Sales department summary" | `generate_pdf` | `report_type=financial, department=Sales` |
