"""
NemoClaw MCP Server
FastAPI application exposing tool endpoints for PDF and image generation.
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes.tools import router as tools_router, files_router
from routes.health import router as health_router

app = FastAPI(
    title="NemoClaw MCP Server",
    description="Model Context Protocol server providing PDF and image generation tools.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow requests from the admin panel and NemoClaw
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
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
        "tools_discovery": "/tools",
    }
