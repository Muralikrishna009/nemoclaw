# TOOLS.md

## NemoClaw — Reports, Spreadsheets & Diagrams

Run from `~/.openclaw/workspace` using `mcporter`.

---

### generate_pdf
Generates a styled PDF report with branded header/footer and KPI cards.

```bash
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=invoice period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=support period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025" department=Engineering
```

| Parameter | Values |
|-----------|--------|
| `report_type` | `financial` \| `summary` \| `invoice` \| `support` |
| `period` | `Q1 2025` \| `Q2 2025` \| `Q3 2025` \| `Q4 2025` |
| `department` | `Sales` \| `Engineering` \| `Marketing` \| `Operations` \| `HR` _(financial only)_ |

**report_type guide:**
- `financial` → monthly revenue, expenses, profit + department budgets
- `summary` → executive KPI overview across all quarters
- `invoice` → invoice ledger with Paid / Pending / Overdue status
- `support` → ticket stats by priority, category + recent ticket list

**Password:** controlled from Admin Panel → Settings → PDF Password Protection.

---

### generate_excel
Generates a styled multi-sheet `.xlsx` workbook with color-coded cells and frozen headers.

```bash
mcporter call nemoclaw-tools.generate_excel report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_excel report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_excel report_type=invoice period="Q1 2025"
mcporter call nemoclaw-tools.generate_excel report_type=support period="Q1 2025"
mcporter call nemoclaw-tools.generate_excel report_type=financial period="Q1 2025" department=Sales
```

| Parameter | Values |
|-----------|--------|
| `report_type` | `financial` \| `summary` \| `invoice` \| `support` |
| `period` | `Q1 2025` \| `Q2 2025` \| `Q3 2025` \| `Q4 2025` |
| `department` | `Sales` \| `Engineering` \| `Marketing` \| `Operations` \| `HR` _(financial only)_ |

**Sheets per report_type:**

| report_type | Sheets |
|-------------|--------|
| `financial` | Overview (KPIs + revenue breakdown), Departments |
| `summary` | Executive Summary (KPIs + all-quarters table) |
| `invoice` | Invoice Ledger (green=Paid, yellow=Pending, red=Overdue) |
| `support` | Overview, By Priority, By Category, Recent Tickets |

**When to use `generate_excel` vs `generate_pdf`:**
- User says "Excel", "spreadsheet", "xlsx", or "sheet" → `generate_excel`
- User says "PDF", "report", or no format specified → `generate_pdf`

**Password:** controlled from Admin Panel → Settings → Excel Password Protection (separate from PDF).

---

### generate_image
Generates a diagram or chart as a `.png` image.

```bash
mcporter call nemoclaw-tools.generate_image diagram_type=flowchart flow=order_processing
mcporter call nemoclaw-tools.generate_image diagram_type=flowchart flow=onboarding
mcporter call nemoclaw-tools.generate_image diagram_type=flowchart flow=support_ticket
mcporter call nemoclaw-tools.generate_image diagram_type=bar_chart period="Q1 2025"
mcporter call nemoclaw-tools.generate_image diagram_type=org_chart
```

| Parameter | Values |
|-----------|--------|
| `diagram_type` | `flowchart` \| `bar_chart` \| `org_chart` |
| `flow` | `order_processing` \| `onboarding` \| `support_ticket` _(flowchart only)_ |
| `period` | `Q1 2025` \| `Q2 2025` \| `Q3 2025` \| `Q4 2025` _(bar_chart only)_ |

---

### After every tool call
Output the returned `file_path` on its own line so OpenClaw attaches it to the Telegram message:

```
MEDIA:/tmp/filename.pdf
MEDIA:/tmp/filename.xlsx
MEDIA:/tmp/filename.png
```

The line must be on its own — no other text on that line.

---

## Servers

| Service | URL |
|---------|-----|
| MCP REST API | `http://localhost:8000` |
| MCP Swagger UI | `http://localhost:8000/docs` |
| Admin Panel | `http://localhost:3000` |
