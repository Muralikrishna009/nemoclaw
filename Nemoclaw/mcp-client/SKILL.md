---
name: nemoclaw-tools
description: Generate PDF financial reports and diagrams using NemoClaw MCP tools. Use when user asks for reports, charts, flowcharts, or diagrams.
metadata: { "openclaw": { "emoji": "📊" } }
---

# NemoClaw MCP Tools

Use `mcporter` to generate PDF reports and diagrams when users ask for them.
The tools return the file content directly — send it to the user as a file attachment.

## When to Activate

- User asks for a **financial report**, **PDF**, **invoice**, or **summary** → use `generate_pdf_tool`
- User asks for a **chart**, **diagram**, **flowchart**, or **org chart** → use `generate_image_tool`

## How to Call

```bash
# Financial PDF report
mcporter call nemoclaw-tools.generate_pdf_tool report_type=financial period="Q1 2025"

# Summary report
mcporter call nemoclaw-tools.generate_pdf_tool report_type=summary period="Q2 2025"

# Invoice report
mcporter call nemoclaw-tools.generate_pdf_tool report_type=invoice period="Q1 2025"

# Flowchart
mcporter call nemoclaw-tools.generate_image_tool diagram_type=flowchart flow=order_processing

# Bar chart
mcporter call nemoclaw-tools.generate_image_tool diagram_type=bar_chart period="Q2 2025"

# Org chart
mcporter call nemoclaw-tools.generate_image_tool diagram_type=org_chart
```

## What the Tools Return

- `generate_pdf_tool` → returns `file_data` (base64 PDF), `filename`, `mime_type: application/pdf`
- `generate_image_tool` → returns image content directly (PNG)

**Send the result as a file/document attachment to the user — not as a URL or text.**

## Parameters

### generate_pdf_tool
- `report_type`: financial | summary | invoice
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025
- `department`: Sales | Engineering | Marketing | Operations | HR (optional)

### generate_image_tool
- `diagram_type`: flowchart | org_chart | bar_chart
- `flow`: order_processing | onboarding | support_ticket (for flowchart)
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025 (for bar_chart)
