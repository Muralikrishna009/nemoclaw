# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## Session Startup

Before doing anything else:

1. Read `SOUL.md` — who you are and how you operate
2. Read `IDENTITY.md` — your role in this specific project
3. Read `USER.md` — who Murali is and what he's building
4. Read `TOOLS.md` — ports, commands, key file paths for NemoClaw
5. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context

Don't ask permission. Just do it.

## This Project: AltM

You're embedded in a **full-stack MCP system**:

```
OpenClaw (Telegram bot)
  └─ mcp_stdio.py  (stdio transport)
       └─ FastAPI MCP Server (port 8000)
            ├─ pdf_service.py   → ReportLab PDFs
            └─ image_service.py → PIL/graphviz diagrams

Admin Panel (Next.js, port 3000)
  └─ Prisma ORM → PostgreSQL
       └─ Users, Roles, Permissions, Settings
```

When user asks about a feature, trace it end-to-end across these layers before answering.

## Memory

You wake up fresh each session. These files are your continuity:

- **Daily notes:** `memory/YYYY-MM-DD.md` — what happened, decisions made, bugs found
- **Long-term:** captured in the memory system via Claude Code's built-in memory

Capture what matters: schema decisions, deployment gotchas, RBAC edge cases, things to revisit.

## Red Lines

- Don't run `DROP TABLE`, `DELETE FROM` (without WHERE), or `prisma migrate reset` without asking.
- Don't push to remote or restart PM2 on EC2 without explicit instruction.
- Don't commit `.env` files. Not even "just to test".
- `trash` > `rm` for anything you're unsure about.
- When in doubt, ask Murali.

## Safe to do freely

- Read any file, explore the codebase
- Run dev servers locally
- Run `db:push` in dev (not prod)
- Write/edit code, fix bugs, add features as asked
- Search, grep, glob the project

## Ask first

- Prisma migrations on production DB
- Any `git push` or deployment step
- Restarting live PM2 processes on EC2
- Changes to Firebase auth config
- Anything touching the `.env` files in production

## Working in this Codebase

**TypeScript (admin-panel):**
- Next.js App Router — pages in `src/app/`, API routes co-located
- Prisma client in `src/lib/prisma.ts`
- Firebase auth via `src/hooks/useAuth.tsx` + `src/components/AuthGuard.tsx`

**Python (mcp-server, mcp-client):**
- FastAPI with Pydantic models
- Services in `mcp-server/services/` — keep PDF and image logic there
- stdio transport in `mcp_stdio.py` — this is what OpenClaw calls

**Database changes:**
1. Edit `admin-panel/prisma/schema.prisma`
2. Run `npm run db:push` (dev) or `npx prisma migrate dev` (prod-safe)
3. Update seed if new roles/permissions added

## Make It Yours

Add conventions, known bugs, deployment notes, and anything else that makes future sessions faster.
