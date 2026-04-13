"""
NemoClaw MCP Server
FastAPI application exposing REST API endpoints for PDF and image generation.
The stdio MCP interface is handled separately by mcp_stdio.py (used by mcporter/OpenClaw).

Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes.tools import router as tools_router, files_router
from routes.health import router as health_router

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

# REST routes
app.include_router(health_router)
app.include_router(tools_router)
app.include_router(files_router)

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
    }
