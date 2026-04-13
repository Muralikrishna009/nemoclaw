module.exports = {
  apps: [
    // ── Admin Panel (Next.js) ─────────────────────────────────────────────────
    {
      name: "nemoclaw-admin",
      script: "node_modules/.bin/next",
      args: "start",
      cwd: "/home/ubuntu/nemoclaw/admin-panel",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
      env: {
        NODE_ENV: "production",
        PORT: 3000,
      },
    },

    // ── MCP Server (FastAPI / uvicorn) ────────────────────────────────────────
    {
      name: "nemoclaw-mcp",
      script: "venv/bin/uvicorn",
      args: "main:app --host 0.0.0.0 --port 8000 --workers 2",
      cwd: "/home/ubuntu/nemoclaw/mcp-server",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
  ],
};
