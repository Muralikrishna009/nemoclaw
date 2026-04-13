---
name: nemoclaw-tools
description: Generate PDF/Excel reports and diagrams using NemoClaw MCP tools. Use when user asks for reports, spreadsheets, charts, flowcharts, or diagrams.
metadata: { "openclaw": { "emoji": "📊" } }
---

# NemoClaw MCP Tools

Generate financial PDF/Excel reports and diagrams. After calling a tool, output the file path
using the `MEDIA:` directive so OpenClaw attaches it directly to the Telegram reply.

## Format Detection — PDF vs Excel

**Use `generate_pdf` when the user clearly says:**
- "PDF", "report", "generate report", "send report"

**Use `generate_excel` when the user clearly says:**
- "Excel", "spreadsheet", "xlsx", "sheet", "editable", "I want to edit the data"

**When the format is ambiguous — ask before calling any tool:**
> If the user says something like "generate financial report", "send me the numbers",
> "give me the data", or anything without a clear format keyword — DO NOT guess.
> Ask: _"Would you like that as a PDF or an Excel spreadsheet?"_
> Then call the correct tool based on their answer.

**report_type selection (applies to both PDF and Excel):**
- User asks for **financial**, **revenue**, **P&L**, **profit** → `report_type=financial`
- User asks for **summary**, **executive summary**, **overview** → `report_type=summary`
- User asks for **invoices**, **billing**, **payment status** → `report_type=invoice`
- User asks for **support tickets**, **ticket report**, **helpdesk** → `report_type=support`

### Images → `generate_image`
- User asks for a **chart**, **diagram**, **flowchart**, or **org chart** → `generate_image`

> Password protection is managed from the admin panel — applied automatically to all files when enabled.

## How to Call

```bash
# PDF
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=invoice period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=support period="Q1 2025"

# Excel
mcporter call nemoclaw-tools.generate_excel report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_excel report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_excel report_type=invoice period="Q1 2025"
mcporter call nemoclaw-tools.generate_excel report_type=support period="Q1 2025"

# Images
mcporter call nemoclaw-tools.generate_image diagram_type=flowchart flow=order_processing
mcporter call nemoclaw-tools.generate_image diagram_type=bar_chart period="Q2 2025"
mcporter call nemoclaw-tools.generate_image diagram_type=org_chart
```

## IMPORTANT — After every tool call

The tool returns a `file_path`. You MUST output it using the MEDIA directive on its own line
so OpenClaw attaches the file to the Telegram message:

```
MEDIA:/tmp/financial_abc123.pdf
```

The line must be on its own — no other text on that line. Example full response:

```
Here is your Q1 2025 Financial Report:

MEDIA:/tmp/financial_abc123.pdf

Let me know if you need any other reports!
```

## Parameters

### generate_pdf / generate_excel
- `report_type`: financial | summary | invoice | support
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025
- `department`: Sales | Engineering | Marketing | Operations | HR (optional, financial only)

### generate_image
- `diagram_type`: flowchart | org_chart | bar_chart
- `flow`: order_processing | onboarding | support_ticket (for flowchart)
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025 (for bar_chart)

## Excel Sheets per Report Type

| report_type | Sheets |
|-------------|--------|
| financial | Overview (KPIs + revenue), Departments |
| summary | Executive Summary (KPIs + quarterly table) |
| invoice | Invoice Ledger (color-coded by status) |
| support | Overview, By Priority, By Category, Recent Tickets |
