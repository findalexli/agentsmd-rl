#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose-skills

# Idempotency guard
if grep -qF "If template initialization fails because the template source is unavailable, tel" "skills/capabilities/create-dashboard/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/capabilities/create-dashboard/SKILL.md b/skills/capabilities/create-dashboard/SKILL.md
@@ -8,205 +8,97 @@ description: >
 tags: [content, design]
 ---
 
-You are helping the user build a custom dashboard from a starter template. The dashboard lives in the sandbox, is served on port 3847 by a single Express process (which also serves the React SPA — no CORS), and is viewable in the Gooseworks "App" tab.
+You are helping the user build a custom dashboard from the Gooseworks dashboard template.
+The app must run on port `3847` from a single Express process that serves both API routes
+and the built React UI so it appears in the Gooseworks App tab.
 
-**Use this template.** Never re-implement the dashboard in Python, Flask, raw HTML, Next.js, or anything else — always clone the template repo and customize it. The template uses React + Vite + Tailwind + Express on a single port.
+## Non-negotiable constraints
 
-**Paths are sandbox-agnostic — always use `$HOME`.**
-Gooseworks runs on two sandbox providers:
-- Daytona → home is `/home/daytona`, workspace at `/home/daytona/workspace`.
-- E2B → home is `/home/user`, workspace at `/home/user/workspace`.
+1. Always use the template workflow (React + Vite + Tailwind + Express). Do not rebuild this in another framework.
+2. Use sandbox-agnostic paths via `$HOME` and `$HOME/workspace` only.
+3. Keep the active project in `$HOME/dashboard` (outside the workspace mount).
+4. Mirror only source files to `$HOME/workspace/dashboard-src` for persistence.
+5. Never place dependencies, build output, or VCS metadata in the mirror.
+6. Use one runtime port (`3847`) and one server process. No separate frontend dev server.
 
-**Every path in this skill uses `$HOME` and `$HOME/workspace`** so the same commands work on both. Never hardcode `/home/daytona/...` or `/home/user/...`.
+## State handling
 
-**Critical path rules — never violate these.**
+Before editing, inspect:
+- whether `$HOME/dashboard` exists
+- whether `$HOME/workspace/dashboard-src` exists
+- whether dependencies are already installed in `$HOME/dashboard`
 
-1. **Working dir is OUTSIDE the S3 mount.** The dashboard project lives at `$HOME/dashboard/`. `$HOME/workspace/` is an S3 FUSE mount — putting `node_modules` or `dist/` there is pathological (every file syncs to S3, adds minutes to every command, costs money). The mount has no ignore patterns, so "just exclude" is not an option.
-2. **Only the source files get mirrored to S3**, at `$HOME/workspace/dashboard-src/`. That mirror contains `src/`, `server.js`, `package.json`, `tsconfig.json`, `vite.config.ts`, `tailwind.config.ts`, `postcss.config.js`, `index.html`, `.gitignore`, `README.md` — and nothing else. No `node_modules`, no `dist`, no `.git`.
-3. **Single-port Express.** Port 3847 serves both the built SPA (`dist/public/`) and `/api/*`. Sandbox preview URLs give each port its own subdomain — running frontend and backend on separate ports breaks with CORS. Never add a Vite dev server. Only `vite build` + `node server.js`.
+Then follow this decision flow:
+- Dashboard exists with dependencies: move to customization.
+- Dashboard missing but mirror exists: restore from mirror into `$HOME/dashboard`, install deps, build, start server, verify health.
+- Both missing: initialize from the official Gooseworks dashboard template, install deps, then continue.
+- Dashboard exists without dependencies: install deps, then continue.
 
----
-
-## Step 1 — Detect state
-
-Figure out what's already there before doing anything:
-
-```bash
-ls -la "$HOME/dashboard" 2>/dev/null || echo "NO_DASHBOARD"
-ls -la "$HOME/workspace/dashboard-src" 2>/dev/null || echo "NO_MIRROR"
-```
-
-Four possible states:
-
-| `$HOME/dashboard` | `$HOME/workspace/dashboard-src` | What to do |
-|---|---|---|
-| exists with `node_modules` | anything | Skip to **Step 3** (Customize) |
-| missing | exists | Go to **Step 2b** (Restore) |
-| missing | missing | Go to **Step 2a** (Fresh setup) |
-| exists but no `node_modules` | anything | Run `npm install` then go to Step 3 |
-
----
-
-## Step 2a — Fresh setup (first time for this agent)
-
-Clone the template repo and install dependencies:
-
-```bash
-git clone --depth 1 https://github.com/gooseworks-ai/dashboard-template.git "$HOME/dashboard"
-cd "$HOME/dashboard"
-rm -rf .git
-npm install
-```
-
-**If the clone fails** (repo not yet public), ask the user to check back once the repo is live. Do not try to scaffold the template from memory — getting the single-port Express + Vite build pipeline right is too easy to break.
-
----
-
-## Step 2b — Restore from mirror (after sandbox restart)
-
-The agent's source lives in S3 at `$HOME/workspace/dashboard-src/`. Rehydrate it:
-
-```bash
-mkdir -p "$HOME/dashboard"
-rsync -a --delete --exclude node_modules --exclude dist --exclude .git \
-  "$HOME/workspace/dashboard-src/" "$HOME/dashboard/"
-cd "$HOME/dashboard"
-npm install
-npx vite build
-pkill -f "node server.js" || true
-nohup node server.js > /tmp/dashboard.log 2>&1 &
-```
-
-Verify it's up: `curl -s http://localhost:3847/api/health`. Then tell the user "Your dashboard is back up." Done.
+If template initialization fails because the template source is unavailable, tell the user to retry once it is available. Do not hand-roll a replacement template.
 
----
-
-## Step 3 — Understand what the user wants
-
-Before writing any code:
-
-1. **Ask** what they want to see if it's not obvious. Examples:
-   - "A sales dashboard with MRR, new deals this week, and a pipeline chart"
-   - "Churn by cohort"
-   - "Campaign performance: opens, clicks, replies"
-2. **Check what data exists** using the `query_database` MCP tool:
-   ```sql
-   SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
-   ```
-   Then for each relevant table, look at its columns with `PRAGMA table_info(<table>)`.
-3. **Confirm the plan** with the user before coding if the request is vague. One sentence: "I'll add a Revenue page with MRR and a weekly trend chart using `deals` and `payments`. Sound good?"
-
----
-
-## Step 4 — Customize the template
-
-The template layout (under `$HOME/dashboard/`):
-
-```
-$HOME/dashboard/
-├── server.js                  ← Express: /api/query + static SPA on port 3847
-├── src/
-│   ├── App.tsx                ← add routes here
-│   ├── pages/Overview.tsx     ← default landing page
-│   ├── pages/...              ← add one file per page
-│   └── components/
-│       ├── Layout.tsx         ← sidebar nav — add NavLinks here for new pages
-│       ├── MetricCard.tsx
-│       └── Chart.tsx          ← recharts LineChart wrapper
-└── src/lib/api.ts             ← runQuery() helper that calls /api/query
-```
-
-**For each page the user needs:**
-1. Create `src/pages/<Name>.tsx`. Use `runQuery("SELECT ...")` from `src/lib/api.ts` to fetch data. Compose `MetricCard` + `Chart` + plain JSX.
-2. Add the route in `src/App.tsx`.
-3. Add a `NavLink` in `src/components/Layout.tsx`.
-
-**For specialized queries** where a raw `SELECT` is awkward (aggregations, joins, parameterized queries), add a dedicated `/api/*` route in `server.js` and fetch it from the page. Keep these endpoints read-only — no writes from the dashboard.
-
-**Style rules** (match the stone palette, match Gooseworks aesthetic):
-- Stone palette only — `text-stone-500`, `border-stone-200`, `bg-stone-50`. No gray/zinc/slate.
-- `font-normal` default, `text-xs` or `text-sm` preferred.
-- `shadow-none`, minimal borders.
-- Recharts with `stroke="#44403c"` (stone-700) and `stroke="#f5f5f4"` for grid.
-
----
+## Discovery and planning
 
-## Step 5 — Build and serve
+Before coding:
+1. Clarify what the user wants to visualize if unclear.
+2. Inspect database schema with `query_database`:
+   - list tables
+   - inspect columns for relevant tables
+3. If the request is vague, confirm a one-sentence implementation plan.
 
-```bash
-cd "$HOME/dashboard"
-npx vite build
-pkill -f "node server.js" || true
-nohup node server.js > /tmp/dashboard.log 2>&1 &
-sleep 1
-curl -s http://localhost:3847/api/health
-```
+## Implementation guidance
 
-If the health check returns `{"ok":true,"db":true}`, you're live. If `"db":false`, the sandbox is missing `AGENT_DB_URL` / `AGENT_DB_TOKEN` — tell the user and stop; they may need to enable an agent database first.
+Template structure to use:
+- `server.js` for API routes and static serving.
+- `src/App.tsx` for route registration.
+- `src/components/Layout.tsx` for sidebar navigation entries.
+- `src/pages/*` for page implementations.
+- `src/lib/api.ts` (`runQuery`) for data access from pages.
 
----
-
-## Step 6 — Persist source to S3
+For each new page:
+1. Create a page component in `src/pages`.
+2. Pull data using `runQuery` or a dedicated read-only API route when SQL becomes complex.
+3. Add route wiring in `src/App.tsx`.
+4. Add navigation in `src/components/Layout.tsx`.
 
-Without this, the dashboard disappears on sandbox restart. Only mirror the source files — never `node_modules` or `dist`:
+Keep all dashboard endpoints read-only.
 
-```bash
-# First: clean up anything that shouldn't be in the S3 mount.
-rm -rf "$HOME/workspace/dashboard" \
-       "$HOME/workspace/dashboard-src/node_modules" \
-       "$HOME/workspace/dashboard-src/dist" \
-       "$HOME/workspace/dashboard-src/.git" 2>/dev/null || true
+## Visual style rules
 
-mkdir -p "$HOME/workspace/dashboard-src"
-rsync -a --delete \
-  --exclude node_modules --exclude dist --exclude .git \
-  "$HOME/dashboard/" "$HOME/workspace/dashboard-src/"
-```
+- Use the stone palette only (for example: `text-stone-*`, `border-stone-*`, `bg-stone-*`).
+- Prefer compact typography (`text-xs` or `text-sm`) with `font-normal`.
+- Keep borders minimal and avoid heavy shadows.
+- For Recharts lines/grids, stay within the stone color family.
 
-**Verify nothing heavy leaked into S3:**
+## Build, run, and verify
 
-```bash
-du -sh "$HOME/workspace/dashboard-src"
-# Expected: < 1 MB. If it's >10 MB, something (probably node_modules) leaked —
-# delete the offending dirs and re-run the rsync.
-```
+After changes:
+1. Run a production build.
+2. Restart the existing dashboard server process cleanly.
+3. Start the server that serves both API and UI on `3847`.
+4. Verify health via `/api/health`.
 
----
+Interpret health:
+- `ok=true` and `db=true`: dashboard is live.
+- `db=false`: inform the user that agent DB credentials/config are missing and stop further DB-dependent work.
 
-## Step 7 — Tell the user
+## Persistence to workspace mirror
 
-Close with something like:
+After each successful change:
+1. Ensure mirror destination is `$HOME/workspace/dashboard-src`.
+2. Sync source files from `$HOME/dashboard` into the mirror.
+3. Exclude dependency/build/VCS folders and files (for example dependency directory, build directory, and `.git`).
+4. Verify mirror size stays small (roughly under 1 MB; if it grows very large, clean leaked heavy folders and sync again).
 
-> Your dashboard is live. Open the **App** tab in the Gooseworks sidebar to see it. It auto-refreshes when I make changes — just tell me what to add, remove, or tweak.
-
----
+The mirror should include source and config files needed to recreate the project quickly after restart.
 
-## Iteration loop (what to do when the user asks for changes)
+## Completion message
 
-When the user asks for a change ("add a churn chart", "make the title bigger", "show only last 30 days"):
-
-1. Edit the relevant files in `$HOME/dashboard/src/` (and `server.js` only if the query is new and complex).
-2. Rebuild + restart:
-   ```bash
-   cd "$HOME/dashboard"
-   npx vite build
-   pkill -f "node server.js" || true
-   nohup node server.js > /tmp/dashboard.log 2>&1 &
-   ```
-3. Mirror back to S3 (Step 6).
-4. Tell the user "Done — the App tab will refresh shortly."
-
-The iframe in the App tab reloads automatically after your message completes. Never ask the user to hit refresh.
-
----
+End with a direct status message that the dashboard is live in the App tab and ready for further edits.
 
-## Safety & correctness checklist
+## Iteration loop
 
-- ✅ All paths use `$HOME` — works on both Daytona and E2B sandboxes.
-- ✅ Single port 3847. Express serves both SPA and API.
-- ✅ No Vite dev server. Only `vite build`.
-- ✅ Dashboard lives at `$HOME/dashboard/` — **outside** the S3 FUSE mount at `$HOME/workspace/`. Do not put `node_modules` inside the mount.
-- ✅ Source mirrored to `$HOME/workspace/dashboard-src/` for restart persistence.
-- ✅ Read-only queries. Do not expose write endpoints. The dashboard is for visualization.
-- ✅ Stone palette, minimal borders, `font-normal`, `text-xs`/`text-sm`.
-- ✅ Kill the old server before starting a new one (`pkill -f "node server.js"`). Don't leave zombies.
+For every follow-up tweak:
+1. Edit relevant files in `$HOME/dashboard`.
+2. Rebuild and restart the single server on `3847`.
+3. Re-sync source-only files to `$HOME/workspace/dashboard-src`.
+4. Tell the user the update is done and that the App tab will refresh.
PATCH

echo "Gold patch applied."
