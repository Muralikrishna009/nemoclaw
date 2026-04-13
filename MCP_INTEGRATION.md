# Connecting OpenClaw to NemoClaw MCP Server

## Important: How OpenClaw Uses MCP

OpenClaw uses **stdio transport** — it spawns the MCP server as a child process
and communicates via stdin/stdout (JSON-RPC 2.0).

> HTTP MCP servers are currently ignored by OpenClaw with the error
> *"only stdio MCP servers are supported right now"*.
> That is why we have `mcp_stdio.py` — a dedicated stdio entry point.

```
OpenClaw
  │  spawns as child process
  ▼
mcp_stdio.py  (stdin/stdout JSON-RPC)
  │  imports and calls
  ▼
services/pdf_service.py
services/image_service.py
  │  saves files to
  ▼
outputs/pdfs/  outputs/images/
  │  served over HTTP by
  ▼
main.py (FastAPI — port 8000)
  │  file_url returned to OpenClaw
  ▼
OpenClaw sends file to user
```

---

## Step 1 — Install MCP SDK in the venv

On your EC2:
```bash
cd ~/nemoclaw/Nemoclaw/mcp-server
source venv/bin/activate
pip install -r requirements.txt   # now includes mcp[cli]==1.6.0
```

---

## Step 2 — Test the stdio server manually

```bash
cd ~/nemoclaw/Nemoclaw/mcp-server
source venv/bin/activate
python mcp_stdio.py
```

It will wait silently — that is correct. It is ready to receive JSON-RPC over stdin.
Press `Ctrl+C` to stop. If no errors appear, the server is working.

---

## Step 3 — Add to OpenClaw config

OpenClaw reads `~/.openclaw/openclaw.json`. Run:

```bash
# Create or edit the config
nano ~/.openclaw/openclaw.json
```

Paste this:
```json
{
  "mcpServers": {
    "nemoclaw": {
      "command": "python",
      "args": ["/home/ubuntu/nemoclaw/Nemoclaw/mcp-server/mcp_stdio.py"],
      "transport": "stdio",
      "env": {
        "BASE_URL": "http://localhost:8000",
        "PYTHONPATH": "/home/ubuntu/nemoclaw/Nemoclaw/mcp-server"
      }
    }
  }
}
```

> **Important:** Use the full absolute path to `mcp_stdio.py`.
> Use `which python` inside the venv to get the full Python path if needed.

---

## Step 4 — Use the venv Python (recommended)

Instead of `python`, point OpenClaw at the venv's Python directly
so it uses the correct packages:

```bash
# Get the full path
source ~/nemoclaw/Nemoclaw/mcp-server/venv/bin/activate
which python
# Output: /home/ubuntu/nemoclaw/Nemoclaw/mcp-server/venv/bin/python
```

Update the config to use that path:
```json
{
  "mcpServers": {
    "nemoclaw": {
      "command": "/home/ubuntu/nemoclaw/Nemoclaw/mcp-server/venv/bin/python",
      "args": ["/home/ubuntu/nemoclaw/Nemoclaw/mcp-server/mcp_stdio.py"],
      "transport": "stdio",
      "env": {
        "BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

---

## Step 5 — Restart OpenClaw gateway

```bash
openclaw gateway restart

# Verify the server is registered
openclaw mcp list
```

You should see `nemoclaw` in the list with status `connected`.

---

## Step 6 — Verify tools are available

```bash
openclaw mcp list-tools nemoclaw
```

Expected output:
```
nemoclaw tools:
  - generate_pdf_tool   Generate a PDF financial report
  - generate_image_tool Generate a diagram or chart image
```

---

## Step 7 — Make sure FastAPI is running

The stdio server generates files and saves them locally.
The file URLs it returns point to the FastAPI server (port 8000).
OpenClaw uses those URLs to download and send files to users.

```bash
# FastAPI must be running via PM2
pm2 status   # mcp-server should be online

# Test a file URL works
curl http://localhost:8000/health
```

---

## How OpenClaw Will Use the Tools

Once connected, OpenClaw's LLM automatically decides when to call the tools
based on what the user says. No extra code needed.

| User says | Tool called | 
|-----------|------------|
| "Generate Q2 financial report" | `generate_pdf_tool(report_type="financial", period="Q2 2025")` |
| "Show me the invoice list" | `generate_pdf_tool(report_type="invoice")` |
| "Draw the order processing flowchart" | `generate_image_tool(diagram_type="flowchart", flow="order_processing")` |
| "Bar chart for Q3 revenue" | `generate_image_tool(diagram_type="bar_chart", period="Q3 2025")` |
| "Show the company org chart" | `generate_image_tool(diagram_type="org_chart")` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: mcp` | Run `pip install mcp[cli]==1.6.0` in the venv |
| `ModuleNotFoundError: services` | Make sure `PYTHONPATH` is set in config or use the full venv Python path |
| Server not in `openclaw mcp list` | Check `~/.openclaw/openclaw.json` syntax and restart gateway |
| File URL not reachable | Make sure FastAPI (`mcp-server`) is running via PM2 on port 8000 |
| `only stdio MCP servers supported` | You are using HTTP transport — switch to the stdio config above |
