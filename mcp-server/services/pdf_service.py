"""
PDF generation service using ReportLab.
Generates financial reports (financial, summary, invoice) from dummy data.
"""

import os
import uuid
import urllib.request
import json
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from reportlab.lib.pdfencrypt import StandardEncryption

from dummy_data.financial import (
    QUARTERLY_REVENUE, DEPARTMENTS, INVOICES, SUMMARY_STATS, SUPPORT_TICKETS
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

_ADMIN_URL = os.getenv("ADMIN_PANEL_URL", "http://localhost:3000")


def _get_pdf_password() -> str | None:
    """Fetch PDF password setting from admin panel. Returns password string or None."""
    try:
        req = urllib.request.Request(
            f"{_ADMIN_URL}/api/settings",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        if data.get("pdf_password_enabled") == "true" and data.get("pdf_password"):
            return data["pdf_password"]
    except Exception:
        pass
    return None

# ── Brand colours ──────────────────────────────────────────────────────────────
PRIMARY    = colors.HexColor("#1a1a2e")
ACCENT     = colors.HexColor("#0f3460")
HIGHLIGHT  = colors.HexColor("#e94560")
LIGHT_BG   = colors.HexColor("#f8f9fa")
BORDER     = colors.HexColor("#dee2e6")
GREEN      = colors.HexColor("#27ae60")
TEXT_MUTED = colors.HexColor("#888888")
WHITE      = colors.white

# Usable width on A4 with 2 cm margins each side
_PW = 17 * cm


# ── Styles ─────────────────────────────────────────────────────────────────────

def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="BannerTitle",
        fontSize=22,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name="BannerSub",
        fontSize=10,
        textColor=colors.HexColor("#aaaacc"),
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=12,
        textColor=PRIMARY,
        fontName="Helvetica-Bold",
        spaceAfter=0,
        spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name="KPILabel",
        fontSize=7,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name="KPIValue",
        fontSize=13,
        textColor=PRIMARY,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name="BodySmall",
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    ))
    return styles


# ── Header / Footer ────────────────────────────────────────────────────────────

def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Page header bar ────────────────────────────────────────────────────────
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, h - 1.7 * cm, w, 1.7 * cm, fill=1, stroke=0)
    # Accent bottom stripe
    canvas.setFillColor(HIGHLIGHT)
    canvas.rect(0, h - 1.7 * cm, w, 0.13 * cm, fill=1, stroke=0)
    # Company name
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(WHITE)
    canvas.drawString(2 * cm, h - 1.1 * cm, "NemoClaw Financial Platform")
    # Date (right-aligned)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#aaaacc"))
    canvas.drawRightString(w - 2 * cm, h - 1.1 * cm, datetime.now().strftime("%B %d, %Y"))

    # ── Page footer bar ────────────────────────────────────────────────────────
    canvas.setFillColor(LIGHT_BG)
    canvas.rect(0, 0, w, 1.5 * cm, fill=1, stroke=0)
    canvas.setFillColor(BORDER)
    canvas.rect(2 * cm, 1.5 * cm, w - 4 * cm, 0.04 * cm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(2 * cm, 0.6 * cm, "Confidential — For internal use only")
    canvas.drawCentredString(w / 2, 0.6 * cm, f"Page {doc.page}")
    canvas.drawRightString(w - 2 * cm, 0.6 * cm, "NemoClaw \u00a9 2025")

    canvas.restoreState()


# ── Reusable flowable builders ─────────────────────────────────────────────────

def _banner(title_text: str, sub_text: str, styles) -> Table:
    """Full-width dark title banner with subtitle."""
    data = [
        [Paragraph(title_text, styles["BannerTitle"])],
        [Paragraph(sub_text,   styles["BannerSub"])],
    ]
    t = Table(data, colWidths=[_PW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING",    (0, 0), (0, 0),   18),
        ("BOTTOMPADDING", (0, 0), (0, 0),   6),
        ("TOPPADDING",    (0, 1), (0, 1),   4),
        ("BOTTOMPADDING", (0, 1), (0, 1),   18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return t


def _section_header(text: str, styles) -> Table:
    """Section header with a 3-pt coloured left accent bar."""
    data = [["", Paragraph(text, styles["SectionHeader"])]]
    t = Table(data, colWidths=[0.3 * cm, _PW - 0.3 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0),   ACCENT),
        ("LEFTPADDING",  (0, 0), (0, 0),   0),
        ("RIGHTPADDING", (0, 0), (0, 0),   0),
        ("LEFTPADDING",  (1, 0), (1, 0),   10),
        ("RIGHTPADDING", (1, 0), (1, 0),   0),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _kpi_row(items: list, styles) -> Table:
    """
    Coloured KPI card row.
    items = [(label, value_str, header_bg_color), ...]
    """
    col_w = _PW / len(items)
    labels = [Paragraph(lbl, styles["KPILabel"]) for lbl, _, _ in items]
    values = [Paragraph(val, styles["KPIValue"]) for _, val, _ in items]

    t = Table([labels, values], colWidths=[col_w] * len(items))
    style_cmds = [
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("BOX",          (0, 0), (-1, -1), 1, ACCENT),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, BORDER),
    ]
    for i, (_, _, bg) in enumerate(items):
        style_cmds.append(("BACKGROUND", (i, 0), (i, 0), bg))
        style_cmds.append(("BACKGROUND", (i, 1), (i, 1), LIGHT_BG))
    t.setStyle(TableStyle(style_cmds))
    return t


def _table_style(header_bg=None) -> TableStyle:
    """Standard reusable table style."""
    return TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  header_bg or PRIMARY),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ALIGN",        (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN",        (0, 0), (0, -1),  "LEFT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDER),
        ("BOX",          (0, 0), (-1, -1), 1, ACCENT),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ])


# ── Financial Report ───────────────────────────────────────────────────────────

def _make_doc(filepath: str, password: str | None = None):
    encrypt = StandardEncryption(password, ownerPassword="", strength=128) if password else None
    kwargs = dict(
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2.6 * cm, bottomMargin=2.6 * cm,
    )
    if encrypt:
        kwargs["encrypt"] = encrypt
    return SimpleDocTemplate(filepath, **kwargs)


def generate_financial_report(title: str, period: str, department: str | None = None, password: str | None = None) -> str:
    filename = f"financial_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = _make_doc(filepath, password)
    styles   = _build_styles()
    elements = []

    # Title banner
    elements.append(_banner(
        title or "Financial Report",
        f"Period: {period}  \u2022  Generated {datetime.now().strftime('%B %d, %Y')}",
        styles,
    ))
    elements.append(HRFlowable(width="100%", thickness=3, color=HIGHLIGHT, spaceAfter=14))

    # KPI row
    elements.append(_section_header("Key Metrics", styles))
    elements.append(Spacer(1, 8))
    elements.append(_kpi_row([
        ("TOTAL REVENUE",  f"${SUMMARY_STATS['total_revenue']:,.0f}",   ACCENT),
        ("TOTAL EXPENSES", f"${SUMMARY_STATS['total_expenses']:,.0f}",  ACCENT),
        ("NET PROFIT",     f"${SUMMARY_STATS['net_profit']:,.0f}",      GREEN),
        ("PROFIT MARGIN",  f"{SUMMARY_STATS['profit_margin']}%",        ACCENT),
        ("YoY GROWTH",     f"{SUMMARY_STATS['yoy_growth']}%",           HIGHLIGHT),
    ], styles))
    elements.append(Spacer(1, 18))

    # Revenue breakdown
    quarter_data = QUARTERLY_REVENUE.get(period, list(QUARTERLY_REVENUE.values())[0])
    elements.append(_section_header(f"Revenue Breakdown \u2014 {period}", styles))
    elements.append(Spacer(1, 8))
    rev_rows = [["Month", "Revenue", "Expenses", "Profit", "Margin"]]
    for row in quarter_data:
        margin = round((row["profit"] / row["revenue"]) * 100, 1)
        rev_rows.append([
            row["month"],
            f"${row['revenue']:,.0f}",
            f"${row['expenses']:,.0f}",
            f"${row['profit']:,.0f}",
            f"{margin}%",
        ])
    totals = {k: sum(r[k] for r in quarter_data) for k in ("revenue", "expenses", "profit")}
    rev_rows.append([
        "TOTAL",
        f"${totals['revenue']:,.0f}",
        f"${totals['expenses']:,.0f}",
        f"${totals['profit']:,.0f}",
        f"{round(totals['profit'] / totals['revenue'] * 100, 1)}%",
    ])
    t2 = Table(rev_rows, colWidths=[4.5 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 2.9 * cm])
    ts2 = _table_style()
    ts2.add("BACKGROUND", (0, len(rev_rows) - 1), (-1, len(rev_rows) - 1),
            colors.HexColor("#e8f5e9"))
    ts2.add("FONTNAME",   (0, len(rev_rows) - 1), (-1, len(rev_rows) - 1), "Helvetica-Bold")
    ts2.add("TEXTCOLOR",  (0, len(rev_rows) - 1), (-1, len(rev_rows) - 1), PRIMARY)
    t2.setStyle(ts2)
    elements.append(t2)
    elements.append(Spacer(1, 18))

    # Department breakdown
    elements.append(_section_header("Department Budget Overview", styles))
    elements.append(Spacer(1, 8))
    depts = {department: DEPARTMENTS[department]} \
        if department and department in DEPARTMENTS else DEPARTMENTS
    dept_rows = [["Department", "Budget", "Spent", "Remaining", "Headcount"]]
    for name, d in depts.items():
        dept_rows.append([
            name,
            f"${d['budget']:,.0f}",
            f"${d['spent']:,.0f}",
            f"${d['budget'] - d['spent']:,.0f}",
            str(d["headcount"]),
        ])
    t3 = Table(dept_rows, colWidths=[4.3 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 3.1 * cm])
    t3.setStyle(_table_style(header_bg=ACCENT))
    elements.append(t3)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Summary Report ─────────────────────────────────────────────────────────────

def generate_summary_report(title: str, period: str, password: str | None = None, **kwargs) -> str:
    filename = f"summary_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = _make_doc(filepath, password)
    styles   = _build_styles()
    elements = []

    elements.append(_banner(
        title or "Executive Summary",
        f"Period: {period}  \u2022  {datetime.now().strftime('%B %d, %Y')}",
        styles,
    ))
    elements.append(HRFlowable(width="100%", thickness=3, color=HIGHLIGHT, spaceAfter=14))

    # Performance KPIs (2 rows of 4)
    elements.append(_section_header("Performance Overview", styles))
    elements.append(Spacer(1, 8))
    elements.append(_kpi_row([
        ("TOTAL REVENUE",  f"${SUMMARY_STATS['total_revenue']:,.0f}",  ACCENT),
        ("NET PROFIT",     f"${SUMMARY_STATS['net_profit']:,.0f}",     GREEN),
        ("ACTIVE CLIENTS", str(SUMMARY_STATS["active_clients"]),       ACCENT),
        ("NEW CLIENTS",    str(SUMMARY_STATS["new_clients"]),          ACCENT),
    ], styles))
    elements.append(Spacer(1, 6))
    elements.append(_kpi_row([
        ("TOTAL EXPENSES", f"${SUMMARY_STATS['total_expenses']:,.0f}", ACCENT),
        ("PROFIT MARGIN",  f"{SUMMARY_STATS['profit_margin']}%",       ACCENT),
        ("YoY GROWTH",     f"{SUMMARY_STATS['yoy_growth']}%",          HIGHLIGHT),
        ("PERIOD",         period,                                       PRIMARY),
    ], styles))
    elements.append(Spacer(1, 18))

    # All-quarters table
    elements.append(_section_header("Quarterly Performance", styles))
    elements.append(Spacer(1, 8))
    q_rows = [["Quarter", "Revenue", "Expenses", "Profit", "Margin"]]
    for q, months in QUARTERLY_REVENUE.items():
        rev = sum(m["revenue"] for m in months)
        exp = sum(m["expenses"] for m in months)
        prf = sum(m["profit"] for m in months)
        q_rows.append([q, f"${rev:,.0f}", f"${exp:,.0f}", f"${prf:,.0f}",
                        f"{round(prf / rev * 100, 1)}%"])
    t = Table(q_rows, colWidths=[3.6 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm, 3.2 * cm])
    t.setStyle(_table_style(header_bg=ACCENT))
    elements.append(t)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Invoice Report ─────────────────────────────────────────────────────────────

def generate_invoice_report(title: str, period: str, password: str | None = None, **kwargs) -> str:
    filename = f"invoice_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = _make_doc(filepath, password)
    styles   = _build_styles()
    elements = []

    elements.append(_banner(
        title or "Invoice Report",
        f"Period: {period}  \u2022  {datetime.now().strftime('%B %d, %Y')}",
        styles,
    ))
    elements.append(HRFlowable(width="100%", thickness=3, color=HIGHLIGHT, spaceAfter=14))

    # Summary KPIs
    total  = sum(i["amount"] for i in INVOICES)
    paid   = sum(i["amount"] for i in INVOICES if i["status"] == "Paid")
    pend   = sum(i["amount"] for i in INVOICES if i["status"] == "Pending")
    overdue = sum(i["amount"] for i in INVOICES if i["status"] == "Overdue")
    elements.append(_kpi_row([
        ("TOTAL INVOICED", f"${total:,.0f}",   ACCENT),
        ("COLLECTED",      f"${paid:,.0f}",    GREEN),
        ("PENDING",        f"${pend:,.0f}",    ACCENT),
        ("OVERDUE",        f"${overdue:,.0f}", HIGHLIGHT),
    ], styles))
    elements.append(Spacer(1, 18))

    elements.append(_section_header("Invoice Ledger", styles))
    elements.append(Spacer(1, 8))

    inv_rows = [["Invoice ID", "Client", "Amount", "Status", "Date"]]
    for inv in INVOICES:
        inv_rows.append([
            inv["id"], inv["client"],
            f"${inv['amount']:,.0f}",
            inv["status"], inv["date"],
        ])
    inv_rows.append(["", "TOTAL", f"${total:,.0f}", "", ""])

    status_colors = {
        "Paid":    colors.HexColor("#d4edda"),
        "Pending": colors.HexColor("#fff3cd"),
        "Overdue": colors.HexColor("#f8d7da"),
    }
    t = Table(inv_rows, colWidths=[2.8 * cm, 4.5 * cm, 3 * cm, 3 * cm, 3.7 * cm])
    base_ts = _table_style()
    # Total row styling
    base_ts.add("BACKGROUND", (0, len(inv_rows) - 1), (-1, len(inv_rows) - 1),
                colors.HexColor("#e8f5e9"))
    base_ts.add("FONTNAME",   (0, len(inv_rows) - 1), (-1, len(inv_rows) - 1), "Helvetica-Bold")
    base_ts.add("TEXTCOLOR",  (0, len(inv_rows) - 1), (-1, len(inv_rows) - 1), PRIMARY)
    # Per-status row colouring
    for i, inv in enumerate(INVOICES, start=1):
        bg = status_colors.get(inv["status"])
        if bg:
            base_ts.add("BACKGROUND", (3, i), (3, i), bg)
    t.setStyle(base_ts)
    elements.append(t)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Support Tickets Report ─────────────────────────────────────────────────────

def generate_support_report(title: str, period: str, password: str | None = None, **kwargs) -> str:
    filename = f"support_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = _make_doc(filepath, password)
    styles   = _build_styles()
    elements = []
    st       = SUPPORT_TICKETS

    elements.append(_banner(
        title or "Support Tickets Report",
        f"Period: {period}  \u2022  {datetime.now().strftime('%B %d, %Y')}",
        styles,
    ))
    elements.append(HRFlowable(width="100%", thickness=3, color=HIGHLIGHT, spaceAfter=14))

    # KPI row
    elements.append(_section_header("Overview", styles))
    elements.append(Spacer(1, 8))
    elements.append(_kpi_row([
        ("TOTAL TICKETS",  str(st["stats"]["total"]),                  ACCENT),
        ("OPEN",           str(st["stats"]["open"]),                   HIGHLIGHT),
        ("IN PROGRESS",    str(st["stats"]["in_progress"]),            ACCENT),
        ("RESOLVED",       str(st["stats"]["resolved"]),               GREEN),
        ("AVG RESOLUTION", f"{st['stats']['avg_resolution_hours']}h",  ACCENT),
    ], styles))
    elements.append(Spacer(1, 6))
    elements.append(_kpi_row([
        ("CLOSED",         str(st["stats"]["closed"]),                 ACCENT),
        ("SLA BREACH",     f"{st['stats']['sla_breach_rate']}%",       HIGHLIGHT),
        ("CSAT SCORE",     f"{st['stats']['csat_score']} / 5.0",       GREEN),
        ("PERIOD",         period,                                       PRIMARY),
    ], styles))
    elements.append(Spacer(1, 18))

    # By Priority
    elements.append(_section_header("Tickets by Priority", styles))
    elements.append(Spacer(1, 8))
    pri_rows = [["Priority", "Total", "Resolved", "Open", "Avg Resolution"]]
    for r in st["by_priority"]:
        pri_rows.append([
            r["priority"],
            str(r["count"]),
            str(r["resolved"]),
            str(r["count"] - r["resolved"]),
            f"{r['avg_hours']}h",
        ])
    t_pri = Table(pri_rows, colWidths=[4 * cm, 3 * cm, 3 * cm, 3 * cm, 4 * cm])
    t_pri.setStyle(_table_style(header_bg=ACCENT))
    elements.append(t_pri)
    elements.append(Spacer(1, 18))

    # By Category
    elements.append(_section_header("Tickets by Category", styles))
    elements.append(Spacer(1, 8))
    cat_rows = [["Category", "Total", "Resolved", "Open", "Resolution Rate"]]
    for r in st["by_category"]:
        rate = round(r["resolved"] / r["count"] * 100, 1) if r["count"] else 0
        cat_rows.append([
            r["category"],
            str(r["count"]),
            str(r["resolved"]),
            str(r["count"] - r["resolved"]),
            f"{rate}%",
        ])
    t_cat = Table(cat_rows, colWidths=[5 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm])
    t_cat.setStyle(_table_style(header_bg=ACCENT))
    elements.append(t_cat)
    elements.append(Spacer(1, 18))

    # Recent tickets
    elements.append(_section_header("Recent Tickets", styles))
    elements.append(Spacer(1, 8))
    rec_rows = [["Ticket ID", "Subject", "Priority", "Status", "Agent", "Hours"]]
    status_colors = {
        "Resolved":    colors.HexColor("#d4edda"),
        "Closed":      colors.HexColor("#e2e3e5"),
        "In Progress": colors.HexColor("#fff3cd"),
        "Open":        colors.HexColor("#f8d7da"),
    }
    for r in st["recent"]:
        rec_rows.append([
            r["id"], r["subject"], r["priority"],
            r["status"], r["agent"],
            f"{r['hours']}h" if r["hours"] else "—",
        ])
    t_rec = Table(rec_rows, colWidths=[2.2 * cm, 6.2 * cm, 2.2 * cm, 2.5 * cm, 2.2 * cm, 1.7 * cm])
    base_ts = _table_style()
    for i, r in enumerate(st["recent"], start=1):
        bg = status_colors.get(r["status"])
        if bg:
            base_ts.add("BACKGROUND", (3, i), (3, i), bg)
    t_rec.setStyle(base_ts)
    elements.append(t_rec)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return filepath


# ── Dispatcher ─────────────────────────────────────────────────────────────────

REPORT_GENERATORS = {
    "financial":      generate_financial_report,
    "summary":        generate_summary_report,
    "invoice":        generate_invoice_report,
    "support":        generate_support_report,
    "support_tickets": generate_support_report,
}


def generate_pdf(report_type: str, title: str, params: dict) -> str:
    period     = params.get("period", "Q1 2025")
    department = params.get("department")
    # Always use the admin panel setting — overrides anything the LLM passes
    password   = _get_pdf_password()
    generator  = REPORT_GENERATORS.get(report_type)
    if generator is None:
        return f"ERROR: Unknown report_type '{report_type}'. Supported: {', '.join(REPORT_GENERATORS)}"
    return generator(title=title, period=period, department=department, password=password)
