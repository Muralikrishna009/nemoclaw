"""
Tool routes exposed to NemoClaw (and any MCP client).
POST /tools/generate-pdf
POST /tools/generate-image
GET  /files/{filename}   — serve generated files
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional

from services.pdf_service import generate_pdf
from services.image_service import generate_image

router = APIRouter(prefix="/tools", tags=["Tools"])

OUTPUTS_ROOT = os.path.join(os.path.dirname(__file__), "..", "outputs")


# ── Request / Response models ─────────────────────────────────────────────────

class PDFRequest(BaseModel):
    report_type: Literal["financial", "summary", "invoice"] = Field(
        "financial",
        description="Type of report to generate",
    )
    title: Optional[str] = Field(None, description="Custom report title")
    params: dict = Field(
        default_factory=lambda: {"period": "Q1 2025"},
        description="Extra params: period (e.g. 'Q1 2025'), department (optional)",
    )


class ImageRequest(BaseModel):
    diagram_type: Literal["flowchart", "org_chart", "bar_chart"] = Field(
        "flowchart",
        description="Type of diagram",
    )
    title: Optional[str] = Field(None, description="Diagram title")
    params: dict = Field(
        default_factory=dict,
        description="Extra params: flow (order_processing|onboarding|support_ticket), period (for bar_chart)",
    )
    nodes: Optional[list[str]] = Field(None, description="Custom node list (flowchart only)")
    edges: Optional[list[list[str]]] = Field(None, description="Custom edge list [[src,dst], ...] (flowchart only)")


class ToolResponse(BaseModel):
    success: bool
    file_url: str
    file_path: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate-pdf", response_model=ToolResponse)
async def generate_pdf_endpoint(body: PDFRequest):
    try:
        filepath = generate_pdf(
            report_type=body.report_type,
            title=body.title or f"{body.report_type.title()} Report",
            params=body.params,
        )
        filename = os.path.basename(filepath)
        return ToolResponse(
            success=True,
            file_url=f"/files/pdfs/{filename}",
            file_path=filepath,
            message=f"{body.report_type.title()} report generated successfully.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-image", response_model=ToolResponse)
async def generate_image_endpoint(body: ImageRequest):
    try:
        filepath = generate_image(
            diagram_type=body.diagram_type,
            title=body.title or f"{body.diagram_type.replace('_', ' ').title()}",
            params=body.params,
            nodes=body.nodes,
            edges=body.edges,
        )
        filename = os.path.basename(filepath)
        return ToolResponse(
            success=True,
            file_url=f"/files/images/{filename}",
            file_path=filepath,
            message=f"{body.diagram_type.replace('_', ' ').title()} generated successfully.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── File serving ──────────────────────────────────────────────────────────────

files_router = APIRouter(prefix="/files", tags=["Files"])


@files_router.get("/pdfs/{filename}")
async def serve_pdf(filename: str):
    filepath = os.path.join(OUTPUTS_ROOT, "pdfs", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)


@files_router.get("/images/{filename}")
async def serve_image(filename: str):
    filepath = os.path.join(OUTPUTS_ROOT, "images", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="image/png", filename=filename)
