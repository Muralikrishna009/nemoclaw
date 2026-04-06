# NemoClaw — Full Stack Setup

## Architecture

```
NemoClaw (EC2 Telegram bot)
        │
        ▼  REST calls
MCP Server  (FastAPI · port 8000)
        │  generates files
        ▼
  outputs/pdfs/  outputs/images/

Admin Panel (Next.js · port 3000)
        │
        ▼  Prisma ORM
  PostgreSQL (port 5432)
```

---

## 1. PostgreSQL Setup

### macOS (Homebrew)
```bash
brew install postgresql@16
brew services start postgresql@16
# Add to PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Create the database
createdb nemoclaw_db
```

### Verify
```bash
psql nemoclaw_db -c "SELECT version();"
```

---

## 2. MCP Server (FastAPI)

```bash
cd mcp-server

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Start server
uvicorn main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

### Test endpoints
```bash
# Health check
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/tools

# Generate a financial PDF
curl -X POST http://localhost:8000/tools/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "financial",
    "title": "Q1 2025 Financial Report",
    "params": { "period": "Q1 2025", "department": "Sales" }
  }'

# Generate a summary PDF
curl -X POST http://localhost:8000/tools/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "summary",
    "title": "Annual Executive Summary",
    "params": { "period": "Q4 2025" }
  }'

# Generate an invoice PDF
curl -X POST http://localhost:8000/tools/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "invoice",
    "params": { "period": "Q1 2025" }
  }'

# Generate a flowchart (default: order processing)
curl -X POST http://localhost:8000/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "flowchart",
    "title": "Order Processing Flow",
    "params": { "flow": "order_processing" }
  }'

# Generate a bar chart
curl -X POST http://localhost:8000/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "bar_chart",
    "title": "Q2 2025 Revenue vs Expenses",
    "params": { "period": "Q2 2025" }
  }'

# Generate an org chart
curl -X POST http://localhost:8000/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "org_chart",
    "title": "Company Structure"
  }'

# Custom flowchart with your own nodes
curl -X POST http://localhost:8000/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "flowchart",
    "title": "Custom Flow",
    "nodes": ["Start", "Process", "Review", "Done"],
    "edges": [["Start","Process"],["Process","Review"],["Review","Done"]]
  }'

# Download generated file (use file_url from response)
curl http://localhost:8000/files/pdfs/<filename>.pdf -o report.pdf
curl http://localhost:8000/files/images/<filename>.png -o chart.png
```

---

## 3. Firebase Setup

1. Go to https://console.firebase.google.com
2. Create a new project (e.g. `nemoclaw-admin`)
3. Go to **Authentication** → **Sign-in method** → Enable **Email/Password**
4. Go to **Authentication** → **Users** → **Add user** → create your admin account
5. Go to **Project Settings** → **Your apps** → click **Web** (`</>`) → Register app
6. Copy the config values for the next step

---

## 4. Admin Panel (Next.js)

```bash
cd admin-panel

# Install dependencies
npm install

# Copy and fill env file
cp .env.example .env.local
```

Edit `.env.local`:
```env
DATABASE_URL="postgresql://postgres:password@localhost:5432/nemoclaw_db"

NEXT_PUBLIC_FIREBASE_API_KEY="your-api-key"
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
NEXT_PUBLIC_FIREBASE_PROJECT_ID="your-project-id"
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="your-project.appspot.com"
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
NEXT_PUBLIC_FIREBASE_APP_ID="your-app-id"

MCP_SERVER_URL="http://localhost:8000"
```

### Database migration and seed
```bash
# Push schema to database
npm run db:push

# Seed default roles, permissions, and sample users
npm run db:seed

# Optional: open Prisma Studio to inspect data
npm run db:studio
```

### Start dev server
```bash
npm run dev
```

Admin panel: http://localhost:3000

Sign in with the Firebase user you created in step 3.

---

## 5. RBAC Logic

| Role  | generate_pdf | generate_image |
|-------|-------------|----------------|
| admin | ✅           | ✅              |
| user  | ✅           | ❌              |

Rules:
- Only `isActive = true` users can use tools
- Permissions are role-based (managed in the Permissions page)
- NemoClaw checks user status + role permissions before calling MCP

### Checking user access (NemoClaw integration example)
```python
import httpx

async def check_user_can_use_tool(telegram_id: str, tool: str) -> bool:
    """Call this from NemoClaw before calling an MCP tool."""
    async with httpx.AsyncClient() as client:
        res = await client.get("http://localhost:3000/api/users")
        users = res.json()
        user = next((u for u in users if u["telegramId"] == telegram_id), None)
        if not user or not user["isActive"]:
            return False
        perms = [rp["permission"]["name"] for rp in user["role"]["rolePermissions"]]
        return tool in perms

async def call_mcp_tool(tool_endpoint: str, payload: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"http://localhost:8000/tools/{tool_endpoint}", json=payload)
        return res.json()
```

---

## 6. Project Structure

```
Nemoclaw/
├── mcp-server/
│   ├── main.py                   # FastAPI app entry point
│   ├── requirements.txt
│   ├── routes/
│   │   ├── tools.py              # /tools/generate-pdf, /tools/generate-image, /files/*
│   │   └── health.py             # /health, /tools (discovery)
│   ├── services/
│   │   ├── pdf_service.py        # ReportLab PDF generation
│   │   └── image_service.py      # PIL flowchart/chart generation
│   ├── dummy_data/
│   │   └── financial.py          # All dummy data (revenue, invoices, departments, flows)
│   └── outputs/
│       ├── pdfs/                 # Generated PDFs
│       └── images/               # Generated PNGs
│
└── admin-panel/
    ├── prisma/
    │   ├── schema.prisma         # DB schema
    │   └── seed.ts               # Seed script
    ├── src/
    │   ├── app/
    │   │   ├── api/
    │   │   │   ├── users/        # GET, POST /api/users
    │   │   │   │   └── [id]/     # GET, PATCH, DELETE /api/users/:id
    │   │   │   ├── roles/        # GET /api/roles
    │   │   │   │   └── [id]/permissions/  # PUT role permissions
    │   │   │   └── permissions/  # GET /api/permissions
    │   │   ├── login/            # Firebase login page
    │   │   ├── dashboard/        # Stats overview
    │   │   ├── users/            # User list, add, edit
    │   │   └── permissions/      # Role-permission matrix
    │   ├── components/
    │   │   ├── Sidebar.tsx
    │   │   ├── AuthGuard.tsx
    │   │   └── UserForm.tsx
    │   ├── hooks/
    │   │   └── useAuth.tsx       # Firebase auth context
    │   └── lib/
    │       ├── firebase.ts
    │       ├── auth.ts
    │       └── prisma.ts
    └── .env.example
```
