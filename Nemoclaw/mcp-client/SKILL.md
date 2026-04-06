---
name: nemoclaw-tools
description: Generate and send PDF financial reports and diagrams directly to users on Telegram.
metadata: { "openclaw": { "emoji": "📊" } }
---

# NemoClaw MCP Tools

Generate and deliver files directly to the user in one tool call.
Always pass the user's `chat_id` from the current Telegram conversation.

## When to Activate

- User asks for a **financial report**, **PDF**, **invoice**, or **summary** → `generate_pdf`
- User asks for a **chart**, **diagram**, **flowchart**, or **org chart** → `generate_image`

## How to Call

```bash
# Financial PDF — file is sent directly to the user
mcporter call nemoclaw-tools.generate_pdf chat_id="<user_chat_id>" report_type=financial period="Q1 2025"

# Summary report
mcporter call nemoclaw-tools.generate_pdf chat_id="<user_chat_id>" report_type=summary period="Q2 2025"

# Invoice
mcporter call nemoclaw-tools.generate_pdf chat_id="<user_chat_id>" report_type=invoice period="Q1 2025"

# Flowchart
mcporter call nemoclaw-tools.generate_image chat_id="<user_chat_id>" diagram_type=flowchart flow=order_processing

# Bar chart
mcporter call nemoclaw-tools.generate_image chat_id="<user_chat_id>" diagram_type=bar_chart period="Q2 2025"

# Org chart
mcporter call nemoclaw-tools.generate_image chat_id="<user_chat_id>" diagram_type=org_chart
```

## Parameters

### generate_pdf
- `chat_id`: Telegram chat ID of the user (required)
- `report_type`: financial | summary | invoice
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025
- `department`: Sales | Engineering | Marketing | Operations | HR (optional)

### generate_image
- `chat_id`: Telegram chat ID of the user (required)
- `diagram_type`: flowchart | org_chart | bar_chart
- `flow`: order_processing | onboarding | support_ticket (for flowchart)
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025 (for bar_chart)

## After Calling

The file is sent directly as a Telegram document. Reply to the user: "Your [report name] has been sent!"
