"""
NemoClaw MCP Stdio Server
─────────────────────────
Entry point for OpenClaw (stdio JSON-RPC transport).
Run directly: python mcp_stdio.py
"""

import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from services.pdf_service import generate_pdf as _gen_pdf
from services.image_service import generate_image as _gen_img
from services.excel_service import generate_excel as _gen_excel

mcp = FastMCP(
    name="NemoClaw Tools",
    instructions=(
        "Tools for generating financial PDF reports and diagrams. "
        "Each tool returns a file_path. Output that path on its own line as MEDIA:<file_path> "
        "so OpenClaw attaches the file to the Telegram reply automatically."
    ),
)


@mcp.tool()
def generate_pdf(
    report_type: str = "financial",
    period: str = "Q1 2025",
    department: str = "",
) -> dict:
    """
    Generate a PDF report. Choose report_type based on what the user asks for:

    - "financial"  → revenue, expenses, profit by month + department budgets
                     Use when: user asks for financial report, revenue report, P&L, profit report
    - "summary"    → executive summary with all-quarter KPIs
                     Use when: user asks for summary, executive summary, overview, quarterly summary
    - "invoice"    → invoice ledger with Paid/Pending/Overdue status
                     Use when: user asks for invoices, billing, invoice list, payment status
    - "support"    → support ticket stats by priority and category + recent ticket list
                     Use when: user asks for support tickets, ticket report, helpdesk report,
                     customer support, number of tickets, ticket summary

    DO NOT use "financial" for support ticket requests. Pick the matching type above.
    Password protection is controlled by the admin panel — no password param needed here.

    Args:
        report_type: "financial" | "summary" | "invoice" | "support"
        period: "Q1 2025" | "Q2 2025" | "Q3 2025" | "Q4 2025"
        department: Sales | Engineering | Marketing | Operations | HR (optional, for financial only)

    Returns:
        file_path of the generated PDF. Output MEDIA:<file_path> to send it to the user.
    """
    params = {"period": period}
    if department:
        params["department"] = department

    filepath = _gen_pdf(
        report_type=report_type,
        title=f"{report_type.replace('_', ' ').title()} Report",
        params=params,
    )

    # Copy to /tmp so it's under OpenClaw's allowed media roots
    tmp_path = os.path.join("/tmp", os.path.basename(filepath))
    shutil.copy2(filepath, tmp_path)

    return {
        "success": True,
        "file_path": tmp_path,
        "message": f"{report_type.title()} report for {period} is ready.",
    }


@mcp.tool()
def generate_image(
    diagram_type: str = "flowchart",
    flow: str = "order_processing",
    period: str = "Q1 2025",
) -> dict:
    """
    Generate a diagram or chart image.

    Args:
        diagram_type: "flowchart", "org_chart", or "bar_chart"
        flow: order_processing | onboarding | support_ticket (for flowchart)
        period: e.g. "Q1 2025", "Q2 2025" (for bar_chart)

    Returns:
        file_path of the generated image. Output MEDIA:<file_path> to send it to the user.
    """
    params = {"flow": flow, "period": period}

    filepath = _gen_img(
        diagram_type=diagram_type,
        title=diagram_type.replace("_", " ").title(),
        params=params,
    )

    # Copy to /tmp so it's under OpenClaw's allowed media roots
    tmp_path = os.path.join("/tmp", os.path.basename(filepath))
    shutil.copy2(filepath, tmp_path)

    return {
        "success": True,
        "file_path": tmp_path,
        "message": f"{diagram_type.replace('_', ' ').title()} is ready.",
    }


@mcp.tool()
def generate_excel(
    report_type: str = "financial",
    period: str = "Q1 2025",
    department: str = "",
) -> dict:
    """
    Generate an Excel (.xlsx) workbook. Choose report_type based on what the user asks for:

    - "financial" → multi-sheet: Overview KPIs + revenue breakdown + department budgets
                    Use when: user asks for financial Excel, revenue spreadsheet, P&L spreadsheet
    - "summary"   → executive KPI summary + all-quarters performance table
                    Use when: user asks for summary Excel, overview spreadsheet
    - "invoice"   → invoice ledger with Paid/Pending/Overdue status color coding
                    Use when: user asks for invoice Excel, billing spreadsheet
    - "support"   → 4 sheets: Overview stats, By Priority, By Category, Recent Tickets
                    Use when: user asks for support ticket Excel, helpdesk spreadsheet

    Use generate_excel when user says "Excel", "spreadsheet", "xlsx", or "sheet".
    Use generate_pdf when user says "PDF" or "report" without specifying format.
    Password protection is controlled by the admin panel — applied automatically if enabled.

    Args:
        report_type: "financial" | "summary" | "invoice" | "support"
        period: "Q1 2025" | "Q2 2025" | "Q3 2025" | "Q4 2025"
        department: Sales | Engineering | Marketing | Operations | HR (optional, financial only)

    Returns:
        file_path of the generated .xlsx file. Output MEDIA:<file_path> to send it to the user.
    """
    params = {"period": period}
    if department:
        params["department"] = department

    filepath = _gen_excel(
        report_type=report_type,
        title=f"{report_type.replace('_', ' ').title()} Report",
        params=params,
    )

    tmp_path = os.path.join("/tmp", os.path.basename(filepath))
    shutil.copy2(filepath, tmp_path)

    return {
        "success": True,
        "file_path": tmp_path,
        "message": f"{report_type.replace('_', ' ').title()} Excel for {period} is ready.",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
