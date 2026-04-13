# TOOLS.md - NemoClaw Environment Notes


## MCP Tool Calls (via mcporter)

```bash
# From ~/.openclaw/workspace
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=invoice
mcporter call nemoclaw-tools.generate_pdf report_type=summary
mcporter call nemoclaw-tools.generate_pdf report_type=support_ticket

mcporter call nemoclaw-tools.generate_image diagram_type=flowchart flow=order_processing
mcporter call nemoclaw-tools.generate_image diagram_type=bar_chart period="Q2 2025"
mcporter call nemoclaw-tools.generate_image diagram_type=org_chart
```
