# NemoClaw MCP Tools

Use `mcporter` to call NemoClaw tools when users ask for reports, charts, or diagrams.

## When to use

- User asks for a **financial report**, **PDF report**, **invoice**, or **summary** → use `generate_pdf_tool`
- User asks for a **chart**, **diagram**, **flowchart**, or **org chart** → use `generate_image_tool`

## How to call

```bash
# PDF report
mcporter call nemoclaw-tools.generate_pdf_tool report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf_tool report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_pdf_tool report_type=invoice period="Q1 2025"

# Diagrams
mcporter call nemoclaw-tools.generate_image_tool diagram_type=flowchart flow=order_processing
mcporter call nemoclaw-tools.generate_image_tool diagram_type=bar_chart period="Q2 2025"
mcporter call nemoclaw-tools.generate_image_tool diagram_type=org_chart
```

## Parameters

### generate_pdf_tool
- `report_type`: financial | summary | invoice
- `period`: Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025
- `department`: Sales | Engineering | Marketing | Operations | HR (optional)

### generate_image_tool
- `diagram_type`: flowchart | org_chart | bar_chart
- `flow`: order_processing | onboarding | support_ticket (for flowchart)
- `period`: Q1 2025 | Q2 2025 | ... (for bar_chart)

## After calling

The tool returns a `file_url`. Send that URL back to the user so they can download the file.
Example response: "Here is your report: http://localhost:8000/files/pdfs/financial_abc123.pdf"
