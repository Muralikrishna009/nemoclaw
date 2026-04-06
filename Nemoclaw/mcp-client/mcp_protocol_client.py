"""
MCP Protocol Client — connects to the MCP server using the official MCP protocol (SSE).
Use this if OpenClaw/NemoClaw supports the MCP protocol natively.

If OpenClaw is a simple Python bot, use client.py (REST) instead.
"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


MCP_SSE_URL = "http://localhost:8000/mcp/sse"


async def call_tool(tool_name: str, arguments: dict) -> dict:
    """
    Call any tool on the MCP server using the proper MCP protocol.

    Args:
        tool_name: "generate_pdf_tool" or "generate_image_tool"
        arguments: dict of tool arguments

    Returns:
        Tool result as dict
    """
    async with sse_client(MCP_SSE_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return result


async def list_tools() -> list:
    """Discover all tools available on the MCP server."""
    async with sse_client(MCP_SSE_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools.tools


# ── Convenience wrappers ──────────────────────────────────────────────────────

async def generate_pdf(
    report_type: str = "financial",
    title: str = "",
    period: str = "Q1 2025",
    department: str = "",
) -> dict:
    result = await call_tool("generate_pdf_tool", {
        "report_type": report_type,
        "title": title,
        "period": period,
        "department": department,
    })
    # Parse the text content from MCP result
    import json
    return json.loads(result.content[0].text)


async def generate_image(
    diagram_type: str = "flowchart",
    title: str = "",
    flow: str = "order_processing",
    period: str = "Q1 2025",
    nodes: list = None,
    edges: list = None,
) -> dict:
    args = {
        "diagram_type": diagram_type,
        "title": title,
        "flow": flow,
        "period": period,
    }
    if nodes:
        args["nodes"] = nodes
    if edges:
        args["edges"] = edges

    result = await call_tool("generate_image_tool", args)
    import json
    return json.loads(result.content[0].text)


# ── Quick test ────────────────────────────────────────────────────────────────

async def main():
    print("Discovering tools via MCP protocol...")
    tools = await list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")

    print("\nCalling generate_pdf_tool...")
    result = await generate_pdf(report_type="financial", period="Q2 2025")
    print(f"  Result: {result}")

    print("\nCalling generate_image_tool...")
    result = await generate_image(diagram_type="bar_chart", period="Q2 2025")
    print(f"  Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
