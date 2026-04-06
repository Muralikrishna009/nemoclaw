"""
Proper MCP Protocol layer using the official MCP Python SDK.
Exposes the same tools (generate-pdf, generate-image) over JSON-RPC via SSE.

This is what OpenClaw connects to — it auto-discovers tools via the MCP protocol.

Endpoint: GET/POST http://localhost:8000/mcp/sse
"""

from mcp.server.fastmcp import FastMCP
from services.pdf_service import generate_pdf
from services.image_service import generate_image
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Create the MCP server instance
mcp = FastMCP(
    name="NemoClaw MCP Server",
    instructions=(
        "This server provides tools to generate PDF financial reports "
        "and image diagrams (flowcharts, bar charts, org charts). "
        "Use generate_pdf for financial/summary/invoice reports. "
        "Use generate_image for flowcharts, org charts, and bar charts."
    ),
)


# ── Tool: generate_pdf ────────────────────────────────────────────────────────

@mcp.tool()
def generate_pdf_tool(
    report_type: str = "financial",
    title: str = "",
    period: str = "Q1 2025",
    department: str = "",
) -> dict:
    """
    Generate a PDF financial report and return its download URL.

    Args:
        report_type: Type of report — "financial", "summary", or "invoice"
        title: Custom title for the report (optional)
        period: Reporting period e.g. "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"
        department: Filter by department e.g. "Sales", "Engineering", "Marketing" (optional)

    Returns:
        dict with file_url (download URL) and message
    """
    params = {"period": period or "Q1 2025"}
    if department:
        params["department"] = department

    filepath = generate_pdf(
        report_type=report_type or "financial",
        title=title or f"{report_type.title()} Report",
        params=params,
    )

    filename = os.path.basename(filepath)
    file_url = f"{BASE_URL}/files/pdfs/{filename}"

    return {
        "success": True,
        "file_url": file_url,
        "message": f"{report_type.title()} report generated for {period}.",
        "download": file_url,
    }


# ── Tool: generate_image ──────────────────────────────────────────────────────

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
    Generate a diagram or chart image and return its download URL.

    Args:
        diagram_type: Type of diagram — "flowchart", "org_chart", or "bar_chart"
        title: Custom title for the diagram (optional)
        flow: Flow type for flowcharts — "order_processing", "onboarding", "support_ticket"
        period: Period for bar charts e.g. "Q1 2025", "Q2 2025"
        nodes: Custom node labels for flowchart (optional) e.g. ["Start", "Process", "End"]
        edges: Custom edges for flowchart (optional) e.g. [["Start", "Process"], ["Process", "End"]]

    Returns:
        dict with file_url (download URL) and message
    """
    params = {"flow": flow or "order_processing", "period": period or "Q1 2025"}

    filepath = generate_image(
        diagram_type=diagram_type or "flowchart",
        title=title or diagram_type.replace("_", " ").title(),
        params=params,
        nodes=nodes,
        edges=edges,
    )

    filename = os.path.basename(filepath)
    file_url = f"{BASE_URL}/files/images/{filename}"

    return {
        "success": True,
        "file_url": file_url,
        "message": f"{diagram_type.replace('_', ' ').title()} generated successfully.",
        "download": file_url,
    }
