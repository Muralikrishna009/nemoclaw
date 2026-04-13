from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PDFRequest:
    report_type: str = "financial"       # financial | summary | invoice
    title: Optional[str] = None
    period: str = "Q1 2025"
    department: Optional[str] = None     # Sales | Engineering | Marketing | Operations | HR

    def to_payload(self) -> dict:
        payload = {
            "report_type": self.report_type,
            "title": self.title or f"{self.report_type.title()} Report",
            "params": {"period": self.period},
        }
        if self.department:
            payload["params"]["department"] = self.department
        return payload


@dataclass
class ImageRequest:
    diagram_type: str = "flowchart"      # flowchart | org_chart | bar_chart
    title: Optional[str] = None
    flow: str = "order_processing"       # order_processing | onboarding | support_ticket
    period: str = "Q1 2025"             # used for bar_chart
    nodes: Optional[list] = None        # custom nodes for flowchart
    edges: Optional[list] = None        # custom edges [[src, dst], ...]

    def to_payload(self) -> dict:
        payload = {
            "diagram_type": self.diagram_type,
            "title": self.title or self.diagram_type.replace("_", " ").title(),
            "params": {"flow": self.flow, "period": self.period},
        }
        if self.nodes:
            payload["nodes"] = self.nodes
        if self.edges:
            payload["edges"] = self.edges
        return payload


@dataclass
class ToolResult:
    success: bool
    file_url: str          # e.g. /files/pdfs/report_abc123.pdf
    file_path: str         # absolute path on MCP server
    message: str
    raw_bytes: Optional[bytes] = None   # populated after download()


@dataclass
class UserPermissions:
    allowed: bool
    permissions: list = field(default_factory=list)
    user: Optional[dict] = None
    reason: Optional[str] = None


@dataclass
class ToolInfo:
    name: str
    endpoint: str
    description: str
    params: dict
