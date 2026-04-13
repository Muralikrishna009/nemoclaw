"""
PDF generation service using ReportLab.
Generates financial reports (financial, summary, invoice) from dummy data.
"""

import os
import uuid
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from dummy_data.financial import (
    QUARTERLY_REVENUE, DEPARTMENTS, INVOICES, SUMMARY_STATS
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Brand colors
PRIMARY = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#0f3460")
HIGHLIGHT = colors.HexColor("#e94560")
LIGHT_BG = colors.HexColor("#f8f9fa")
BORDER = colors.HexColor("#dee2e6")


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=6,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="SubTitle",
        fontSize=12,
        textColor=ACCENT,
        spaceAfter=4,
        fontName="Helvetica",
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=13,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="BodySmall",
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="MetricLabel",
        fontSize=10,
        textColor=ACCENT,
        fontName="Helvetica-Bold",
    ))
    return styles


def _header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setFillColor(PRIMARY)
    canvas.rect(2 * cm, A4[1] - 1.8 * cm, A4[0] - 4 * cm, 0.08 * cm, fill=1, stroke=0)
    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawString(2 * cm, 1.2 * cm, "NemoClaw Financial Platform")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}  |  Generated {datetime.now().strftime('%b %d, %Y')}")
    canvas.restoreState()


# ── Financial Report ──────────────────────────────────────────────────────────

def generate_financial_report(title: str, period: str, department: str | None = None) -> str:
    filename = f"financial_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
    )
    styles = _build_styles()
    elements = []

    # Title block
    elements.append(Paragraph(title or "Financial Report", styles["ReportTitle"]))
    elements.append(Paragraph(f"Period: {period}  |  Generated {datetime.now().strftime('%B %d, %Y')}", styles["SubTitle"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=HIGHLIGHT, spaceAfter=16))

    # Key metrics
    elements.append(Paragraph("Key Metrics", styles["SectionHeader"]))
    metrics = [
        ["Total Revenue", "Total Expenses", "Net Profit", "Profit Margin", "YoY Growth"],
        [
            f"${SUMMARY_STATS['total_revenue']:,.0f}",
            f"${SUMMARY_STATS['total_expenses']:,.0f}",
            f"${SUMMARY_STATS['net_profit']:,.0f}",
            f"{SUMMARY_STATS['profit_margin']}%",
            f"{SUMMARY_STATS['yoy_growth']}%",
        ],
    ]
    t = Table(metrics, colWidths=[3.2 * cm] * 5)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 11),
        ("TEXTCOLOR", (2, 1), (2, 1), colors.HexColor("#27ae60")),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    # Revenue breakdown
    quarter_data = QUARTERLY_REVENUE.get(period, list(QUARTERLY_REVENUE.values())[0])
    elements.append(Paragraph(f"Revenue Breakdown — {period}", styles["SectionHeader"]))
    rev_table_data = [["Month", "Revenue", "Expenses", "Profit", "Margin"]]
    for row in quarter_data:
        margin = round((row["profit"] / row["revenue"]) * 100, 1)
        rev_table_data.append([
            row["month"],
            f"${row['revenue']:,.0f}",
            f"${row['expenses']:,.0f}",
            f"${row['profit']:,.0f}",
            f"{margin}%",
        ])
    totals = {
        "revenue": sum(r["revenue"] for r in quarter_data),
        "expenses": sum(r["expenses"] for r in quarter_data),
        "profit": sum(r["profit"] for r in quarter_data),
    }
    rev_table_data.append([
        "TOTAL",
        f"${totals['revenue']:,.0f}",
        f"${totals['expenses']:,.0f}",
        f"${totals['profit']:,.0f}",
        f"{round(totals['profit']/totals['revenue']*100,1)}%",
    ])
    col_w = [4 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 2.4 * cm]
    t2 = Table(rev_table_data, colWidths=col_w)
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, LIGHT_BG]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f5e9")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 16))

    # Department breakdown (optional filter)
    elements.append(Paragraph("Department Budget Overview", styles["SectionHeader"]))
    dept_data = [["Department", "Budget", "Spent", "Remaining", "Headcount"]]
    depts = {department: DEPARTMENTS[department]} if department and department in DEPARTMENTS else DEPARTMENTS
    for name, d in depts.items():
        remaining = d["budget"] - d["spent"]
        dept_data.append([
            name,
            f"${d['budget']:,.0f}",
            f"${d['spent']:,.0f}",
            f"${remaining:,.0f}",
            str(d["headcount"]),
        ])
    t3 = Table(dept_data, colWidths=[3.8 * cm, 3 * cm, 3 * cm, 3 * cm, 3.2 * cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.append(t3)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Summary Report ────────────────────────────────────────────────────────────

def generate_summary_report(title: str, period: str, **kwargs) -> str:
    filename = f"summary_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
    )
    styles = _build_styles()
    elements = []

    elements.append(Paragraph(title or "Executive Summary", styles["ReportTitle"]))
    elements.append(Paragraph(f"Period: {period}  |  {datetime.now().strftime('%B %d, %Y')}", styles["SubTitle"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=HIGHLIGHT, spaceAfter=16))

    # Stats grid
    elements.append(Paragraph("Performance Overview", styles["SectionHeader"]))
    stats = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Revenue", f"${SUMMARY_STATS['total_revenue']:,.0f}", "Active Clients", str(SUMMARY_STATS['active_clients'])],
        ["Net Profit", f"${SUMMARY_STATS['net_profit']:,.0f}", "New Clients", str(SUMMARY_STATS['new_clients'])],
        ["Profit Margin", f"{SUMMARY_STATS['profit_margin']}%", "YoY Growth", f"{SUMMARY_STATS['yoy_growth']}%"],
    ]
    t = Table(stats, colWidths=[5 * cm, 4 * cm, 5 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    # All quarters summary
    elements.append(Paragraph("Quarterly Performance", styles["SectionHeader"]))
    q_data = [["Quarter", "Revenue", "Expenses", "Profit", "Margin"]]
    for q, months in QUARTERLY_REVENUE.items():
        rev = sum(m["revenue"] for m in months)
        exp = sum(m["expenses"] for m in months)
        prf = sum(m["profit"] for m in months)
        q_data.append([q, f"${rev:,.0f}", f"${exp:,.0f}", f"${prf:,.0f}", f"{round(prf/rev*100,1)}%"])
    t2 = Table(q_data, colWidths=[3.6 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 2.8 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.append(t2)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Invoice Report ────────────────────────────────────────────────────────────

def generate_invoice_report(title: str, period: str, **kwargs) -> str:
    filename = f"invoice_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
    )
    styles = _build_styles()
    elements = []

    elements.append(Paragraph(title or "Invoice Report", styles["ReportTitle"]))
    elements.append(Paragraph(f"Period: {period}  |  {datetime.now().strftime('%B %d, %Y')}", styles["SubTitle"]))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=HIGHLIGHT, spaceAfter=16))

    elements.append(Paragraph("Invoice Ledger", styles["SectionHeader"]))
    inv_data = [["Invoice ID", "Client", "Amount", "Status", "Date"]]
    for inv in INVOICES:
        inv_data.append([inv["id"], inv["client"], f"${inv['amount']:,.0f}", inv["status"], inv["date"]])

    total = sum(i["amount"] for i in INVOICES)
    inv_data.append(["", "TOTAL", f"${total:,.0f}", "", ""])

    t = Table(inv_data, colWidths=[2.8 * cm, 4.5 * cm, 3 * cm, 3 * cm, 3.7 * cm])

    status_colors = {"Paid": colors.HexColor("#d4edda"), "Pending": colors.HexColor("#fff3cd"), "Overdue": colors.HexColor("#f8d7da")}
    row_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, LIGHT_BG]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f5e9")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    for i, inv in enumerate(INVOICES, start=1):
        bg = status_colors.get(inv["status"], colors.white)
        row_styles.append(("BACKGROUND", (3, i), (3, i), bg))
    t.setStyle(TableStyle(row_styles))
    elements.append(t)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Dispatcher ────────────────────────────────────────────────────────────────

REPORT_GENERATORS = {
    "financial": generate_financial_report,
    "summary": generate_summary_report,
    "invoice": generate_invoice_report,
}


def generate_pdf(report_type: str, title: str, params: dict) -> str:
    period = params.get("period", "Q1 2025")
    department = params.get("department")
    generator = REPORT_GENERATORS.get(report_type, generate_financial_report)
    return generator(title=title, period=period, department=department)
