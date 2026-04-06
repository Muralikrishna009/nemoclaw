# NemoClaw — EC2 Setup Guide (Ubuntu)

## Prerequisites Check

```bash
docker --version && node --version && npm --version && python3 --version
```

---

## 1. Install System Dependencies

```bash
# pip and venv
sudo apt install python3-pip python3.12-venv -y
```

---

## 2. PostgreSQL (Docker)

```bash
# Pull image
docker pull postgres:16

# Run container
docker run -d \
  --name nemoclaw-postgres \
  -e POSTGRES_USER=nemoclaw \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=nemoclaw_db \
  -p 5432:5432 \
  --restart unless-stopped \
  postgres:16

# Verify
docker ps | grep nemoclaw-postgres
docker exec -it nemoclaw-postgres pg_isready -U nemoclaw

# Optional: connect to psql shell
docker exec -it nemoclaw-postgres psql -U nemoclaw -d nemoclaw_db
# Exit: \q
```

### Useful Docker commands
```bash
docker stop nemoclaw-postgres
docker start nemoclaw-postgres
docker logs nemoclaw-postgres
```

---

## 3. MCP Server (FastAPI — port 8000)

```bash
cd ~/nemoclaw/Nemoclaw/mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup env
cp .env.example .env

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify: `curl http://localhost:8000/health`

Swagger UI: `http://<EC2-PUBLIC-IP>:8000/docs`

---

## 4. Firebase Setup

1. Go to https://console.firebase.google.com
2. Create a new project (e.g. `nemoclaw-admin`)
3. Go to **Authentication** → **Sign-in method** → Enable **Email/Password**
4. Go to **Authentication** → **Users** → **Add user** → create your admin account
5. Go to **Project Settings** → **Your apps** → click **Web** (`</>`) → Register app
6. Copy the config values for the next step

---

## 5. Admin Panel (Next.js — port 3000)

```bash
cd ~/nemoclaw/Nemoclaw/admin-panel

# Install dependencies
npm install

# Setup env
cp .env.example .env.local
nano .env.local
```

Fill in `.env.local`:
```env
DATABASE_URL="postgresql://nemoclaw:yourpassword@localhost:5432/nemoclaw_db"

NEXT_PUBLIC_FIREBASE_API_KEY="your-api-key"
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
NEXT_PUBLIC_FIREBASE_PROJECT_ID="your-project-id"
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="your-project.appspot.com"
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
NEXT_PUBLIC_FIREBASE_APP_ID="your-app-id"

MCP_SERVER_URL="http://localhost:8000"
```

```bash
# Push schema to database
npx prisma db push

# Seed default roles, permissions, sample users
npm run db:seed

# Run dev server
npm run dev
```

Verify: `curl http://localhost:3000`

---

## 6. Verify Both Services

```bash
# MCP Server
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/tools

# Admin Panel
curl http://localhost:3000
```

---

## 7. EC2 Security Group Ports

Make sure these ports are open in your EC2 Security Group inbound rules:

| Port | Service        |
|------|----------------|
| 22   | SSH            |
| 8000 | MCP Server     |
| 3000 | Admin Panel    |

---

## 8. Quick Test — MCP Endpoints

```bash
# Generate financial PDF
curl -X POST http://localhost:8000/tools/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{"report_type": "financial", "title": "Q1 Report", "params": {"period": "Q1 2025"}}'

# Generate flowchart
curl -X POST http://localhost:8000/tools/generate-image \
  -H "Content-Type: application/json" \
  -d '{"diagram_type": "flowchart", "title": "Order Flow", "params": {"flow": "order_processing"}}'

# Download generated file (replace filename from response)
curl http://localhost:8000/files/pdfs/<filename>.pdf -o report.pdf
curl http://localhost:8000/files/images/<filename>.png -o chart.png
```

---

## 9. Running with PM2

### Install PM2
```bash
npm install -g pm2
```

### Start both apps
```bash
# MCP Server (FastAPI)
pm2 start "source ~/nemoclaw/Nemoclaw/mcp-server/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000" \
  --name mcp-server \
  --cwd ~/nemoclaw/Nemoclaw/mcp-server

# Admin Panel (Next.js) — build first for production
cd ~/nemoclaw/Nemoclaw/admin-panel && npm run build
pm2 start "npm start" \
  --name admin-panel \
  --cwd ~/nemoclaw/Nemoclaw/admin-panel
```

### Check status
```bash
pm2 status
pm2 logs          # all logs
pm2 logs mcp-server
pm2 logs admin-panel
```

### Auto-start on reboot
```bash
pm2 save
pm2 startup       # run the command it outputs with sudo
```

### Useful PM2 commands
```bash
pm2 restart mcp-server
pm2 restart admin-panel
pm2 stop mcp-server
pm2 stop admin-panel
pm2 delete mcp-server    # remove from pm2
pm2 monit                # live dashboard
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ensurepip not available` | `sudo apt install python3.12-venv -y` |
| `pip3 not found` | `sudo apt install python3-pip -y` |
| Postgres not connecting | `docker start nemoclaw-postgres` |
| Port already in use | `sudo lsof -i :8000` then `kill -9 <PID>` |
| Prisma can't connect | Check `DATABASE_URL` in `.env.local` |
