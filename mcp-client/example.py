"""
Example: how OpenClaw uses the MCP client.
Copy this pattern into your bot handlers.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from client import MCPClient
from models import PDFRequest, ImageRequest
from exceptions import RBACError, MCPConnectionError, MCPToolError


# ── Initialize once (at bot startup) ─────────────────────────────────────────

mcp = MCPClient(
    mcp_server_url="http://localhost:8000",
    admin_panel_url="http://localhost:3000",
)


# ── Examples ──────────────────────────────────────────────────────────────────

async def example_generate_pdf_with_rbac():
    """Generate a PDF and enforce RBAC for a Telegram user."""
    telegram_id = "user_001"   # from update.effective_user.id in real bot

    try:
        result = await mcp.generate_pdf(
            request=PDFRequest(
                report_type="financial",
                title="Q2 2025 Financial Report",
                period="Q2 2025",
                department="Sales",
            ),
            telegram_id=telegram_id,   # enforces RBAC
        )
        print(f"PDF generated: {result.file_url}")

        # Download as bytes → send via Telegram
        file_bytes = await mcp.download(result)
        print(f"Downloaded {len(file_bytes)} bytes")

        # In your bot: await update.message.reply_document(io.BytesIO(file_bytes), filename="report.pdf")

    except RBACError as e:
        print(f"Access denied: {e}")
        # In your bot: await update.message.reply_text(str(e))

    except MCPConnectionError as e:
        print(f"Server error: {e}")

    except MCPToolError as e:
        print(f"Tool error: {e}")


async def example_generate_flowchart():
    """Generate an order processing flowchart."""
    telegram_id = "admin_001"

    try:
        result = await mcp.generate_image(
            request=ImageRequest(
                diagram_type="flowchart",
                title="Order Processing Flow",
                flow="order_processing",
            ),
            telegram_id=telegram_id,
        )
        print(f"Image generated: {result.file_url}")
        file_bytes = await mcp.download(result)
        print(f"Downloaded {len(file_bytes)} bytes")

    except RBACError as e:
        print(f"Access denied: {e}")


async def example_generate_bar_chart():
    """Generate a Q3 revenue bar chart."""
    result = await mcp.generate_image(
        request=ImageRequest(
            diagram_type="bar_chart",
            title="Q3 2025 Revenue vs Expenses",
            period="Q3 2025",
        ),
        # No telegram_id = skip RBAC (trusted internal call)
    )
    print(f"Chart: {result.file_url}")


async def example_custom_flowchart():
    """Generate a flowchart with custom nodes."""
    result = await mcp.generate_image(
        request=ImageRequest(
            diagram_type="flowchart",
            title="My Custom Flow",
            nodes=["Start", "Validate", "Process", "Complete"],
            edges=[
                ["Start", "Validate"],
                ["Validate", "Process"],
                ["Process", "Complete"],
            ],
        ),
    )
    print(f"Custom flowchart: {result.file_url}")


async def example_discover_tools():
    """List all tools available on MCP server."""
    tools = await mcp.list_tools()
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")


async def example_health_check():
    """Check MCP server health."""
    status = await mcp.health()
    print(f"MCP status: {status}")


# ── Run all examples ──────────────────────────────────────────────────────────

async def main():
    print("=== Health Check ===")
    await example_health_check()

    print("\n=== Available Tools ===")
    await example_discover_tools()

    print("\n=== PDF with RBAC ===")
    await example_generate_pdf_with_rbac()

    print("\n=== Flowchart ===")
    await example_generate_flowchart()

    print("\n=== Bar Chart ===")
    await example_generate_bar_chart()

    print("\n=== Custom Flowchart ===")
    await example_custom_flowchart()


if __name__ == "__main__":
    asyncio.run(main())
