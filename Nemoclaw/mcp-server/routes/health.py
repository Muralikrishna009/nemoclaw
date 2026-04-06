from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "NemoClaw MCP Server", "timestamp": datetime.utcnow().isoformat()}


@router.get("/tools")
async def list_tools():
    """List all available tools — useful for NemoClaw tool discovery."""
    return {
        "tools": [
            {
                "name": "generate-pdf",
                "endpoint": "POST /tools/generate-pdf",
                "description": "Generate a PDF financial report (financial, summary, invoice)",
                "params": {
                    "report_type": "financial | summary | invoice",
                    "title": "string (optional)",
                    "params": {"period": "Q1 2025 | Q2 2025 | ...", "department": "Sales | Engineering | ... (optional)"},
                },
            },
            {
                "name": "generate-image",
                "endpoint": "POST /tools/generate-image",
                "description": "Generate a diagram or chart (flowchart, org_chart, bar_chart)",
                "params": {
                    "diagram_type": "flowchart | org_chart | bar_chart",
                    "title": "string (optional)",
                    "params": {"flow": "order_processing | onboarding | support_ticket", "period": "Q1 2025 (for bar_chart)"},
                    "nodes": ["list of node labels (flowchart only, optional)"],
                    "edges": [["src", "dst"]],
                },
            },
        ]
    }
