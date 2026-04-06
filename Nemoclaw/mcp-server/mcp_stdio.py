"""
NemoClaw MCP Stdio Server
─────────────────────────
Entry point for OpenClaw (stdio JSON-RPC transport).
Run directly: python mcp_stdio.py
"""

import sys
import os
import json
import http.client
import mimetypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from services.pdf_service import generate_pdf
from services.image_service import generate_image

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

mcp = FastMCP(
    name="NemoClaw Tools",
    instructions=(
        "Tools for generating and sending financial PDF reports and diagrams directly to the user. "
        "Use generate_pdf to create and send PDF reports. "
        "Use generate_image to create and send diagram/chart images. "
        "Always pass the user's chat_id so the file is delivered as a Telegram attachment."
    ),
)


def _send_telegram_document(chat_id: str, filepath: str, caption: str = "") -> dict:
    """Send a local file as a Telegram document."""
    if not TELEGRAM_BOT_TOKEN:
        return {"ok": False, "description": "TELEGRAM_BOT_TOKEN not set"}

    filename = os.path.basename(filepath)
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    boundary = "NemoClawBoundary"

    with open(filepath, "rb") as f:
        file_bytes = f.read()

    def field(name, value):
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        ).encode()

    body = b""
    body += field("chat_id", chat_id)
    if caption:
        body += field("caption", caption)
    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_bytes + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    conn = http.client.HTTPSConnection("api.telegram.org")
    conn.request(
        "POST",
        f"/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
        body=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    resp = conn.getresponse()
    result = json.loads(resp.read().decode())
    conn.close()
    return result


# ── Tool: Generate and Send PDF ───────────────────────────────────────────────

@mcp.tool()
def generate_pdf(
    chat_id: str,
    report_type: str = "financial",
    period: str = "Q1 2025",
    department: str = "",
    title: str = "",
) -> dict:
    """
    Generate a PDF financial report and send it directly to the user on Telegram.

    Args:
        chat_id: Telegram chat ID of the user (required — from current conversation)
        report_type: "financial", "summary", or "invoice"
        period: e.g. "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"
        department: Sales | Engineering | Marketing | Operations | HR (optional)
        title: Custom report title (optional)

    Returns:
        success status
    """
    params = {"period": period or "Q1 2025"}
    if department:
        params["department"] = department

    from services.pdf_service import generate_pdf as _gen
    filepath = _gen(
        report_type=report_type or "financial",
        title=title or f"{(report_type or 'financial').title()} Report",
        params=params,
    )

    result = _send_telegram_document(
        chat_id=chat_id,
        filepath=filepath,
        caption=f"{(report_type or 'financial').title()} Report — {period}",
    )

    if result.get("ok"):
        return {"success": True, "message": f"PDF sent to user."}
    else:
        return {"success": False, "message": f"Telegram error: {result.get('description', str(result))}"}


# ── Tool: Generate and Send Image ─────────────────────────────────────────────

@mcp.tool()
def generate_image(
    chat_id: str,
    diagram_type: str = "flowchart",
    flow: str = "order_processing",
    period: str = "Q1 2025",
    title: str = "",
    nodes: list[str] = None,
    edges: list[list[str]] = None,
) -> dict:
    """
    Generate a diagram or chart and send it directly to the user on Telegram.

    Args:
        chat_id: Telegram chat ID of the user (required — from current conversation)
        diagram_type: "flowchart", "org_chart", or "bar_chart"
        flow: For flowcharts — "order_processing", "onboarding", or "support_ticket"
        period: For bar_chart — e.g. "Q1 2025", "Q2 2025"
        title: Custom diagram title (optional)
        nodes: Custom node labels (optional)
        edges: Custom edges (optional)

    Returns:
        success status
    """
    params = {
        "flow": flow or "order_processing",
        "period": period or "Q1 2025",
    }

    from services.image_service import generate_image as _gen
    filepath = _gen(
        diagram_type=diagram_type or "flowchart",
        title=title or (diagram_type or "flowchart").replace("_", " ").title(),
        params=params,
        nodes=nodes,
        edges=edges,
    )

    result = _send_telegram_document(
        chat_id=chat_id,
        filepath=filepath,
        caption=(diagram_type or "flowchart").replace("_", " ").title(),
    )

    if result.get("ok"):
        return {"success": True, "message": f"Image sent to user."}
    else:
        return {"success": False, "message": f"Telegram error: {result.get('description', str(result))}"}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
