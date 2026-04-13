# NemoClaw — EC2 Operations Guide

## Architecture Overview

```
Telegram User
      │
      ▼
  OpenClaw (Telegram bot gateway)
      │  reads skill from
      ├──────────────────────────────► ~/.openclaw/workspace/  (SKILL.md)
      │
      │  calls tools via mcporter
      ▼
  mcporter (MCP CLI)
      │  reads config from
      ├──────────────────────────────► ~/.openclaw/workspace/config/mcporter.json
      │
      │  spawns as child process (stdio JSON-RPC)
      ▼
  mcp_stdio.py  (/home/ubuntu/nemoclaw/mcp-server/)
      │
      ├── services/pdf_service.py    → ReportLab → outputs/pdfs/
      ├── services/image_service.py  → Pillow    → outputs/images/
      │
      │  fetches PDF password setting from
      ├──────────────────────────────► Admin Panel API (port 3000) /api/settings
      │
      │  copies file to /tmp/ → returns file_path
      ▼
  OpenClaw reads MEDIA:/tmp/file → sends to Telegram user

  ─────────────────────────────────────────────────────────────

  Admin Panel (Next.js — port 3000)
      │
      └── Prisma ORM ──► PostgreSQL (Docker — port 5432)

  MCP Server REST API (FastAPI — port 8000)
      │  serves generated files over HTTP
      └── /files/pdfs/<name>.pdf
          /files/images/<name>.png
```

---

## Services

| Service | Type | Port | Process Manager | CWD |
|---------|------|------|-----------------|-----|
| Admin Panel | Next.js | 3000 | PM2 `nemoclaw-admin` | `/home/ubuntu/nemoclaw/admin-panel` |
| MCP REST API | FastAPI/uvicorn | 8000 | PM2 `nemoclaw-mcp` | `/home/ubuntu/nemoclaw/mcp-server` |
| MCP Stdio | Python child process | — | spawned by mcporter | `/home/ubuntu/nemoclaw/mcp-server` |
| PostgreSQL | Docker | 5432 | Docker `nemoclaw-postgres` | — |

---

## Directory Structure (EC2)

```
/home/ubuntu/nemoclaw/
├── admin-panel/          # Next.js admin panel
│   ├── src/
│   ├── prisma/
│   │   ├── schema.prisma
│   │   └── seed.ts
│   ├── .env.local        # DATABASE_URL + Firebase config
│   ├── .env              # copy of .env.local (Prisma reads this)
│   └── ecosystem.config.js
│
├── mcp-server/           # FastAPI + MCP stdio server
│   ├── main.py           # FastAPI REST API (port 8000)
│   ├── mcp_stdio.py      # stdio MCP server (mcporter spawns this)
│   ├── services/
│   │   ├── pdf_service.py
│   │   └── image_service.py
│   ├── dummy_data/
│   │   └── financial.py
│   ├── routes/
│   ├── outputs/
│   │   ├── pdfs/         # generated PDF files
│   │   └── images/       # generated image files
│   ├── venv/             # Python virtual environment
│   ├── requirements.txt
│   └── .env              # BASE_URL, ADMIN_PANEL_URL
│
└── ecosystem.config.js   # PM2 config for both services

/home/ubuntu/.openclaw/
├── openclaw.json         # OpenClaw gateway config
└── workspace/
    └── config/
        └── mcporter.json  # mcporter MCP server config
```

---

## PM2 — Process Manager

### Check status
```bash
pm2 status
pm2 monit         # live dashboard
```

### Start all services (from project root)
```bash
cd ~/nemoclaw
pm2 start ecosystem.config.js
```

### Restart
```bash
pm2 restart nemoclaw-admin
pm2 restart nemoclaw-mcp
pm2 restart all
```

### Stop
```bash
pm2 stop nemoclaw-admin
pm2 stop nemoclaw-mcp
```

### Logs
```bash
pm2 logs                   # all services
pm2 logs nemoclaw-admin    # admin panel only
pm2 logs nemoclaw-mcp      # MCP server only
pm2 logs --lines 100       # last 100 lines
```

### Auto-start on reboot
```bash
pm2 save
pm2 startup    # run the command it outputs with sudo
```

---

## PostgreSQL (Docker)

### Container management
```bash
docker ps                          # check if running
docker start nemoclaw-postgres     # start
docker stop nemoclaw-postgres      # stop
docker restart nemoclaw-postgres   # restart
docker logs nemoclaw-postgres      # view logs
```

### Connect to database
```bash
docker exec -it nemoclaw-postgres psql -U nemoclaw -d nemoclaw_db
```

### Useful psql commands
```sql
\dt                  -- list tables
\d "User"            -- describe User table
SELECT * FROM "User";
SELECT * FROM "Setting";
\q                   -- quit
```

### Create container from scratch
```bash
docker run -d \
  --name nemoclaw-postgres \
  -e POSTGRES_USER=nemoclaw \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=nemoclaw_db \
  -p 5432:5432 \
  --restart unless-stopped \
  postgres:16
```

---

## Admin Panel (Next.js)

### Environment file (`/home/ubuntu/nemoclaw/admin-panel/.env.local`)
```env
DATABASE_URL="postgresql://nemoclaw:yourpassword@localhost:5432/nemoclaw_db"

NEXT_PUBLIC_FIREBASE_API_KEY="..."
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="..."
NEXT_PUBLIC_FIREBASE_PROJECT_ID="..."
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="..."
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="..."
NEXT_PUBLIC_FIREBASE_APP_ID="..."

MCP_SERVER_URL="http://localhost:8000"
```

> Prisma reads `.env`, not `.env.local`. Always keep both in sync:
> ```bash
> cp .env.local .env
> ```

### Database commands
```bash
cd ~/nemoclaw/admin-panel

# Push schema changes to database
npx prisma db push

# Seed default data (roles, permissions, settings)
npm run db:seed

# Open Prisma Studio (database GUI)
npx prisma studio
```

### Build and run
```bash
cd ~/nemoclaw/admin-panel
npm install
npm run build
pm2 restart nemoclaw-admin
```

### Access
- URL: `http://<EC2-PUBLIC-IP>:3000`
- Login: Firebase email/password (created in Firebase Console → Authentication → Users)

---

## MCP Server (FastAPI)

### Environment file (`/home/ubuntu/nemoclaw/mcp-server/.env`)
```env
HOST=0.0.0.0
PORT=8000
BASE_URL=http://localhost:8000
ADMIN_PANEL_URL=http://localhost:3000
```

### Virtual environment
```bash
cd ~/nemoclaw/mcp-server
source venv/bin/activate
pip install -r requirements.txt
```

### Run manually (dev)
```bash
cd ~/nemoclaw/mcp-server
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### REST API endpoints
```bash
# Health check
curl http://localhost:8000/health

# List tools
curl http://localhost:8000/tools

# Generate PDF
curl -X POST http://localhost:8000/tools/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{"report_type": "financial", "title": "Q1 Report", "params": {"period": "Q1 2025"}}'

# Generate image
curl -X POST http://localhost:8000/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{"diagram_type": "flowchart", "title": "Order Flow", "params": {"flow": "order_processing"}}'

# Download file
curl http://localhost:8000/files/pdfs/<filename>.pdf -o report.pdf
curl http://localhost:8000/files/images/<filename>.png -o chart.png
```

- Swagger UI: `http://<EC2-PUBLIC-IP>:8000/docs`

---

## mcporter & MCP Stdio

### Config file
`~/.openclaw/workspace/config/mcporter.json`
```json
{
  "mcpServers": {
    "nemoclaw-tools": {
      "command": "/home/ubuntu/nemoclaw/mcp-server/venv/bin/python",
      "args": ["/home/ubuntu/nemoclaw/mcp-server/mcp_stdio.py"],
      "transport": "stdio"
    }
  }
}
```

### mcporter commands
```bash
mcporter list                          # list servers and status
mcporter list --verbose                # with source info
mcporter config list                   # show config details

# Call tools directly
mcporter call nemoclaw-tools.generate_pdf report_type=financial period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=summary period="Q2 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=invoice period="Q1 2025"
mcporter call nemoclaw-tools.generate_pdf report_type=support period="Q1 2025"

mcporter call nemoclaw-tools.generate_image diagram_type=flowchart flow=order_processing
mcporter call nemoclaw-tools.generate_image diagram_type=bar_chart period="Q2 2025"
mcporter call nemoclaw-tools.generate_image diagram_type=org_chart
```

### Test stdio server manually
```bash
/home/ubuntu/nemoclaw/mcp-server/venv/bin/python \
  /home/ubuntu/nemoclaw/mcp-server/mcp_stdio.py
# Should wait silently — Ctrl+C to stop
```

---

## Excel Generation

### Report types (same as PDF)

| `report_type` | Sheets | Use when user asks for |
|---------------|--------|------------------------|
| `financial` | Overview (KPIs + revenue breakdown), Departments | financial Excel, revenue spreadsheet, P&L |
| `summary` | Executive Summary (KPIs + quarterly table) | summary Excel, overview sheet |
| `invoice` | Invoice Ledger (color-coded Paid/Pending/Overdue) | invoice Excel, billing spreadsheet |
| `support` | Overview, By Priority, By Category, Recent Tickets | support ticket Excel, helpdesk sheet |

### Password protection
- Same admin panel setting as PDF — **Settings → Generated Files Password Protection**
- Uses `msoffcrypto-tool` for AES encryption
- Requires `openpyxl==3.1.5` and `msoffcrypto-tool==5.4.2` in venv

### Output directory
```
/home/ubuntu/nemoclaw/mcp-server/outputs/excels/
```

---

## PDF Generation

### Report types

| `report_type` | Content | Use when user asks for |
|---------------|---------|------------------------|
| `financial` | Monthly revenue, expenses, profit + department budgets | financial report, revenue, P&L |
| `summary` | Executive KPIs across all quarters | summary, overview, quarterly summary |
| `invoice` | Invoice ledger (Paid/Pending/Overdue) | invoices, billing, payment status |
| `support` | Ticket stats by priority/category + recent tickets | support tickets, helpdesk report |

### Password protection
- Controlled from **Admin Panel → Settings**
- When enabled, all generated PDFs require the configured password to open
- MCP server fetches the setting from `/api/settings` before each generation
- Uses AES-128 encryption via ReportLab

---

## Image Generation

### Diagram types

| `diagram_type` | Content | Optional params |
|----------------|---------|-----------------|
| `flowchart` | Top-down process flow with colored nodes | `flow`: `order_processing` / `onboarding` / `support_ticket` |
| `bar_chart` | Grouped bar chart: Revenue vs Expenses vs Profit | `period`: Q1–Q4 2025 |
| `org_chart` | CEO → Departments → Sub-teams | — |

---

## OpenClaw Config

`~/.openclaw/openclaw.json` — OpenClaw gateway config (separate from mcporter)

> This file controls OpenClaw itself (bot token, etc.).
> Do **not** use this file to configure mcporter — use `~/.openclaw/workspace/config/mcporter.json` instead.

---

## EC2 Security Group — Required Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 22 | TCP | SSH |
| 3000 | TCP | Admin Panel |
| 8000 | TCP | MCP REST API / Swagger |

---

## Deploy Updates

After pushing code changes from local to EC2:

```bash
# 1. Pull latest code
cd ~/nemoclaw
git pull

# 2. If admin-panel changed
cd ~/nemoclaw/admin-panel
npm install          # if package.json changed
npx prisma db push   # if schema.prisma changed
npm run build
pm2 restart nemoclaw-admin

# 3. If mcp-server changed
cd ~/nemoclaw/mcp-server
source venv/bin/activate
pip install -r requirements.txt   # if requirements.txt changed
pm2 restart nemoclaw-mcp

# 4. mcp_stdio.py changes take effect immediately
# (mcporter spawns a fresh process per call — no restart needed)
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `nemoclaw-tools (offline)` in mcporter | Wrong paths in mcporter.json | Check `~/.openclaw/workspace/config/mcporter.json` paths |
| Admin panel blank / Firebase error | Missing `.env.local` | Recreate `.env.local` and `cp .env.local .env` |
| `DATABASE_URL not found` | Prisma reads `.env` not `.env.local` | `cp .env.local .env` |
| Postgres not connecting | Container stopped | `docker start nemoclaw-postgres` |
| Port already in use | Old process running | `sudo lsof -i :8000` then `kill -9 <PID>` |
| PDF has no content / wrong content | Wrong `report_type` passed | Check SKILL.md trigger mapping |
| PDF password not applying | Admin panel unreachable | Ensure `pm2 status` shows nemoclaw-admin online |
| `ensurepip not available` | Missing venv package | `sudo apt install python3.12-venv -y` |
| PM2 not found | Not installed globally | `npm install -g pm2` |
