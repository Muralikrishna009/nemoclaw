---
name: nemoclaw-tools
description: Generate PDF financial reports and diagrams using NemoClaw MCP tools. Use when user asks for reports, charts, flowcharts, or diagrams.
metadata: { "openclaw": { "emoji": "📊" } }
---

# NemoClaw MCP Tools

Generate financial PDF reports and diagrams. After calling a tool, output the file path using
the `MEDIA:` directive so OpenClaw attaches it directly to the Telegram reply.

## When to Activate

- User asks for a **financial report**, **revenue**, **P&L**, **profit** → `generate_pdf` with `report_type=financial`
- User asks for a **summary**, **executive summary**, **overview** → `generate_pdf` with `report_type=summary`
- User asks for **invoices**, **billing**, **payment status** → `generate_pdf` with `report_type=invoice`
- User asks for **support tickets**, **ticket report**, **helpdesk**, **number of tickets** → `generate_pdf` with `report_type=support`
- User asks for a **chart**, **diagram**, **flowchart**, or **org chart** → `generate_image`
- User asks to **password protect** the PDF → add `password=<value>` to the `generate_pdf` call

## How to Call

```bash
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=invoice period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=support period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025" password="secret123"

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

### generate_pdf
- `report_type`: financial | summary | invoice | support
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025
- `department`: Sales | Engineering | Marketing | Operations | HR (optional, financial only)
- `password`: optional PDF password (e.g. "secret123")

### generate_image
- `diagram_type`: flowchart | org_chart | bar_chart
- `flow`: order_processing | onboarding | support_ticket (for flowchart)
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025 (for bar_chart)
