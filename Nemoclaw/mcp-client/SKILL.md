---
name: nemoclaw-tools
description: Generate PDF financial reports and diagrams using NemoClaw MCP tools. Use when user asks for reports, charts, flowcharts, or diagrams.
metadata: { "openclaw": { "emoji": "📊" } }
---

# NemoClaw MCP Tools

## IMPORTANT — Two-step process

Always call TWO tools in sequence:
1. Generate the file → `generate_pdf_tool` or `generate_image_tool`
2. Send it to the user → `send_file_to_telegram` (use the `file_url` from step 1 and the user's `chat_id`)

Never just return the file URL as text. Always deliver the file as a Telegram attachment.

## When to Activate

- User asks for a **financial report**, **PDF**, **invoice**, or **summary** → `generate_pdf_tool`
- User asks for a **chart**, **diagram**, **flowchart**, or **org chart** → `generate_image_tool`

## Step 1 — Generate

```bash
# Financial PDF
mcporter call nemoclaw-tools.generate_pdf_tool report_type=financial period="Q1 2025"

# Summary
mcporter call nemoclaw-tools.generate_pdf_tool report_type=summary period="Q2 2025"

# Invoice
mcporter call nemoclaw-tools.generate_pdf_tool report_type=invoice period="Q1 2025"

# Flowchart
mcporter call nemoclaw-tools.generate_image_tool diagram_type=flowchart flow=order_processing

# Bar chart
mcporter call nemoclaw-tools.generate_image_tool diagram_type=bar_chart period="Q2 2025"

# Org chart
mcporter call nemoclaw-tools.generate_image_tool diagram_type=org_chart
```

## Step 2 — Send to user (ALWAYS required)

```bash
mcporter call nemoclaw-tools.send_file_to_telegram \
  file_url="<file_url from step 1>" \
  chat_id="<user's Telegram chat_id>" \
  caption="Here is your report"
```

## Parameters

### generate_pdf_tool
- `report_type`: financial | summary | invoice
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025
- `department`: Sales | Engineering | Marketing | Operations | HR (optional)

### generate_image_tool
- `diagram_type`: flowchart | org_chart | bar_chart
- `flow`: order_processing | onboarding | support_ticket (for flowchart)
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025 (for bar_chart)

### send_file_to_telegram
- `file_url`: URL returned by generate_pdf_tool or generate_image_tool
- `chat_id`: Telegram chat ID of the current user
- `caption`: short description of the file (optional)
