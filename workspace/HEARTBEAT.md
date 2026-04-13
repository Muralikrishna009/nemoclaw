# HEARTBEAT.md

# Periodic checks for the NemoClaw project.
# Keep this file small — it's loaded on every heartbeat tick.

## Active checks

- [ ] Are both services healthy? (`GET /health` on port 8000, `GET /` on port 3000)
- [ ] Any new untracked files or uncommitted changes worth noting? (`git status`)
- [ ] Any open TODO/FIXME comments added since last session?

## Notes

- MCP server runs on port 8000, admin panel on port 3000
- Check `mcp-server/outputs/` occasionally — generated PDFs/images accumulate there
- If `pm2 status` shows any process as `errored`, flag it immediately

## Skip heartbeat API calls if this file has no active tasks.
