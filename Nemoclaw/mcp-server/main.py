"""
NemoClaw MCP Server
FastAPI application exposing:
  - REST API endpoints  → used by mcp-client / direct HTTP callers
  - MCP Protocol (SSE)  → used by OpenClaw / Claude Desktop / any MCP-aware agent

Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes.tools import router as tools_router, files_router
from routes.health import router as health_router
from mcp_protocol import mcp  # MCP protocol instance

app = FastAPI(
    title="NemoClaw MCP Server",
    description="MCP server providing PDF and image generation tools.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST routes (used by mcp-client and direct HTTP callers) ──────────────────
app.include_router(health_router)
app.include_router(tools_router)
app.include_router(files_router)

# ── MCP Protocol (SSE) — used by OpenClaw / Claude Desktop ───────────────────
# OpenClaw connects to: http://localhost:8000/mcp/sse
mcp_app = mcp.get_asgi_app()
app.mount("/mcp", mcp_app)

# Ensure output dirs exist
for sub in ("pdfs", "images"):
    os.makedirs(os.path.join("outputs", sub), exist_ok=True)


@app.get("/")
async def root():
    return {
        "service": "NemoClaw MCP Server",
        "docs": "/docs",
        "health": "/health",
        "rest_tools": "/tools",
        "mcp_protocol": "/mcp/sse",   # <-- OpenClaw connects here
    }
