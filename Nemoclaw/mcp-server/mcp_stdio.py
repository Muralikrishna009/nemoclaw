"""
NemoClaw MCP Stdio Server
─────────────────────────
This is the entry point OpenClaw uses. It runs as a child process
spawned by OpenClaw and communicates via stdin/stdout (JSON-RPC 2.0).

DO NOT run this with uvicorn. Run it directly:
    python mcp_stdio.py

OpenClaw config (~/.openclaw/openclaw.json):
{
  "mcpServers": {
    "nemoclaw": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-server/mcp_stdio.py"],
      "transport": "stdio",
      "env": {
        "BASE_URL": "http://localhost:8000"
      }
    }
  }
}
"""

import sys
import os
import base64

# Add mcp-server root to path so services/ and dummy_data/ are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP, Image
from services.pdf_service import generate_pdf
from services.image_service import generate_image

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

mcp = FastMCP(
    name="NemoClaw Tools",
    instructions=(
        "Tools for generating financial PDF reports and diagrams. "
        "Use generate_pdf for financial, summary, or invoice reports. "
        "Use generate_image for flowcharts, org charts, and bar charts. "
        "After generating, send the file directly to the user as a document attachment."
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
    Generate a PDF financial report and return its content for delivery to the user.

    Args:
        report_type: "financial", "summary", or "invoice"
        title: Custom report title (optional)
        period: Reporting period e.g. "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"
        department: Filter by department — "Sales", "Engineering", "Marketing", "Operations", "HR" (optional)

    Returns:
        dict with file_data (base64 PDF), filename, mime_type, and a message.
        Send file_data to the user as a PDF document attachment.
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

    with open(filepath, "rb") as f:
        file_data = base64.b64encode(f.read()).decode("utf-8")

    return {
        "success": True,
        "filename": filename,
        "mime_type": "application/pdf",
        "file_data": file_data,
        "file_url": file_url,
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
) -> Image:
    """
    Generate a diagram or chart image and return it for delivery to the user.

    Args:
        diagram_type: "flowchart", "org_chart", or "bar_chart"
        title: Custom diagram title (optional)
        flow: For flowcharts — "order_processing", "onboarding", or "support_ticket"
        period: For bar_chart — e.g. "Q1 2025", "Q2 2025"
        nodes: Custom node labels for flowchart e.g. ["Start", "Process", "End"] (optional)
        edges: Custom edges e.g. [["Start","Process"],["Process","End"]] (optional)

    Returns:
        Image content — send this directly to the user as a photo or image attachment.
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

    with open(filepath, "rb") as f:
        image_bytes = f.read()

    return Image(data=image_bytes, format="png")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
