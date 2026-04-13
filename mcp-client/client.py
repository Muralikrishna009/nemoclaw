"""
MCPClient — the main interface OpenClaw uses to interact with the MCP server.

Usage:
    from client import MCPClient
    from models import PDFRequest, ImageRequest

    mcp = MCPClient(
        mcp_server_url="http://localhost:8000",
        admin_panel_url="http://localhost:3000",
    )

    # With RBAC
    result = await mcp.generate_pdf(telegram_id="12345", request=PDFRequest(period="Q2 2025"))
    file_bytes = await mcp.download(result)

    # Without RBAC (internal / trusted calls)
    result = await mcp.generate_pdf(request=PDFRequest())
"""

import httpx
from models import PDFRequest, ImageRequest, ToolResult, ToolInfo
from rbac import RBACClient
from exceptions import MCPConnectionError, MCPToolError


class MCPClient:
    def __init__(
        self,
        mcp_server_url: str = "http://localhost:8000",
        admin_panel_url: str = "http://localhost:3000",
        timeout: int = 30,
    ):
        self.base_url = mcp_server_url.rstrip("/")
        self.timeout = timeout
        self.rbac = RBACClient(admin_panel_url)

    # ── Health & Discovery ────────────────────────────────────────────────────

    async def health(self) -> dict:
        """Check if MCP server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.get(f"{self.base_url}/health")
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise MCPConnectionError(f"MCP server unreachable: {e}")

    async def list_tools(self) -> list[ToolInfo]:
        """Discover all tools available on the MCP server."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.get(f"{self.base_url}/tools")
                res.raise_for_status()
                data = res.json()
                return [
                    ToolInfo(
                        name=t["name"],
                        endpoint=t["endpoint"],
                        description=t["description"],
                        params=t["params"],
                    )
                    for t in data.get("tools", [])
                ]
        except httpx.RequestError as e:
            raise MCPConnectionError(f"MCP server unreachable: {e}")

    # ── PDF Tool ──────────────────────────────────────────────────────────────

    async def generate_pdf(
        self,
        request: PDFRequest = None,
        telegram_id: str = None,
    ) -> ToolResult:
        """
        Generate a PDF report.
        Pass telegram_id to enforce RBAC, or omit for internal/trusted calls.
        """
        if telegram_id:
            await self.rbac.enforce(telegram_id, "generate_pdf")

        if request is None:
            request = PDFRequest()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/tools/generate-pdf",
                    json=request.to_payload(),
                )
                res.raise_for_status()
                data = res.json()
        except httpx.RequestError as e:
            raise MCPConnectionError(f"MCP server unreachable: {e}")
        except httpx.HTTPStatusError as e:
            raise MCPToolError(f"PDF generation failed: {e.response.text}")

        return ToolResult(
            success=data["success"],
            file_url=data["file_url"],
            file_path=data["file_path"],
            message=data["message"],
        )

    # ── Image Tool ────────────────────────────────────────────────────────────

    async def generate_image(
        self,
        request: ImageRequest = None,
        telegram_id: str = None,
    ) -> ToolResult:
        """
        Generate a diagram or chart.
        Pass telegram_id to enforce RBAC, or omit for internal/trusted calls.
        """
        if telegram_id:
            await self.rbac.enforce(telegram_id, "generate_image")

        if request is None:
            request = ImageRequest()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/tools/generate-image",
                    json=request.to_payload(),
                )
                res.raise_for_status()
                data = res.json()
        except httpx.RequestError as e:
            raise MCPConnectionError(f"MCP server unreachable: {e}")
        except httpx.HTTPStatusError as e:
            raise MCPToolError(f"Image generation failed: {e.response.text}")

        return ToolResult(
            success=data["success"],
            file_url=data["file_url"],
            file_path=data["file_path"],
            message=data["message"],
        )

    # ── File Download ─────────────────────────────────────────────────────────

    async def download(self, result: ToolResult) -> bytes:
        """
        Download the generated file as bytes.
        Attaches bytes to result.raw_bytes and returns them.
        Useful for sending files directly via Telegram.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}{result.file_url}")
                res.raise_for_status()
                result.raw_bytes = res.content
                return res.content
        except httpx.RequestError as e:
            raise MCPConnectionError(f"Failed to download file: {e}")
