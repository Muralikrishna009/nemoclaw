"""
NemoClaw MCP Stdio Server
─────────────────────────
This is the entry point OpenClaw uses. It runs as a child process
spawned by OpenClaw and communicates via stdin/stdout (JSON-RPC 2.0).

DO NOT run this with uvicorn. Run it directly:
    python mcp_stdio.py
"""

import sys
import os
import base64
import json
import http.client
import mimetypes
import urllib.request
import urllib.parse

# Add mcp-server root to path so services/ and dummy_data/ are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from services.pdf_service import generate_pdf
from services.image_service import generate_image

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

mcp = FastMCP(
    name="NemoClaw Tools",
    instructions=(
        "Tools for generating financial PDF reports and diagrams. "
        "After generating a file, always call send_file_to_telegram to deliver "
        "the actual file to the user as a Telegram document attachment."
    ),
)


# ── Tool: Generate PDF ────────────────────────────────────────────────────────

@mcp.tool()
def generate_pdf_tool(
    report_type: str = "financial",
    title: str = "",
    period: str = "Q1 2025",
    department: str = "",
) -> dict:
    """
    Generate a PDF financial report.

    Args:
        report_type: "financial", "summary", or "invoice"
        title: Custom report title (optional)
        period: Reporting period e.g. "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"
        department: Filter by department — Sales, Engineering, Marketing, Operations, HR (optional)

    Returns:
        dict with file_url. Then call send_file_to_telegram to deliver the file.
    """
    params = {"period": period or "Q1 2025"}
    if department:
        params["department"] = department

    filepath = generate_pdf(
        report_type=report_type or "financial",
        title=title or f"{(report_type or 'financial').title()} Report",
        params=params,
    )

    filename = os.path.basename(filepath)
    file_url = f"{BASE_URL}/files/pdfs/{filename}"

    return {
        "success": True,
        "file_url": file_url,
        "filename": filename,
        "message": f"{(report_type or 'financial').title()} report generated for {period}.",
    }


# ── Tool: Generate Image ──────────────────────────────────────────────────────

@mcp.tool()
def generate_image_tool(
    diagram_type: str = "flowchart",
    title: str = "",
    flow: str = "order_processing",
    period: str = "Q1 2025",
    nodes: list[str] = None,
    edges: list[list[str]] = None,
) -> dict:
    """
    Generate a diagram or chart image.

    Args:
        diagram_type: "flowchart", "org_chart", or "bar_chart"
        title: Custom diagram title (optional)
        flow: For flowcharts — "order_processing", "onboarding", or "support_ticket"
        period: For bar_chart — e.g. "Q1 2025", "Q2 2025"
        nodes: Custom node labels for flowchart e.g. ["Start", "Process", "End"] (optional)
        edges: Custom edges e.g. [["Start","Process"],["Process","End"]] (optional)

    Returns:
        dict with file_url. Then call send_file_to_telegram to deliver the file.
    """
    params = {
        "flow": flow or "order_processing",
        "period": period or "Q1 2025",
    }

    filepath = generate_image(
        diagram_type=diagram_type or "flowchart",
        title=title or (diagram_type or "flowchart").replace("_", " ").title(),
        params=params,
        nodes=nodes,
        edges=edges,
    )

    filename = os.path.basename(filepath)
    file_url = f"{BASE_URL}/files/images/{filename}"

    return {
        "success": True,
        "file_url": file_url,
        "filename": filename,
        "message": f"{(diagram_type or 'flowchart').replace('_', ' ').title()} generated.",
    }


# ── Tool: Send File to Telegram ───────────────────────────────────────────────

@mcp.tool()
def send_file_to_telegram(
    file_url: str,
    chat_id: str,
    caption: str = "",
) -> dict:
    """
    Download a generated file and send it as a Telegram document to the user.
    Always call this after generate_pdf_tool or generate_image_tool.

    Args:
        file_url: The file_url returned by generate_pdf_tool or generate_image_tool
        chat_id: The Telegram chat ID of the user (from the current conversation)
        caption: Short description of the file (optional)

    Returns:
        dict with success status
    """
    bot_token = TELEGRAM_BOT_TOKEN
    if not bot_token:
        return {"success": False, "message": "TELEGRAM_BOT_TOKEN not set in environment."}
    if not chat_id:
        return {"success": False, "message": "chat_id is required."}

    # Download file to /tmp
    filename = os.path.basename(urllib.parse.urlparse(file_url).path)
    tmp_path = os.path.join("/tmp", filename)
    try:
        urllib.request.urlretrieve(file_url, tmp_path)
    except Exception as e:
        return {"success": False, "message": f"Failed to download file: {e}"}

    # Send via Telegram sendDocument
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    boundary = "NemoClawBoundary"

    with open(tmp_path, "rb") as f:
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

    try:
        conn = http.client.HTTPSConnection("api.telegram.org")
        conn.request(
            "POST",
            f"/bot{bot_token}/sendDocument",
            body=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        resp = conn.getresponse()
        result = json.loads(resp.read().decode())
        conn.close()
    except Exception as e:
        return {"success": False, "message": f"Telegram API request failed: {e}"}
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    if result.get("ok"):
        return {"success": True, "message": f"File sent to user (chat {chat_id})."}
    else:
        return {"success": False, "message": f"Telegram error: {result.get('description', str(result))}"}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
