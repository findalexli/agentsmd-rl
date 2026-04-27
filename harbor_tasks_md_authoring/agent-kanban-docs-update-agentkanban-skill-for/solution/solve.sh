#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-kanban

# Idempotency guard
if grep -qF "- Repo management: `ak create repo` registers repo at tenant level. `ak get repo" "CLAUDE.md" && grep -qF "- Always create a PR and submit via `task review --pr-url` when your work produc" "skills/agent-kanban/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -39,7 +39,7 @@ In QA mode, flag any code that doesn't match DESIGN.md.
 - SSE: TransformStream-based, 2s poll for 25s (CF Workers limit), Last-Event-ID resume via log ID → timestamp resolution (sse.ts). Emits typed events (`event: log` for task_logs, `event: message` for messages).
 - Messages: `messages` table for human ↔ agent chat. `agent_id` = agent CLI session ID (used for `claude --resume`). D1 as message bus — daemon polls for human messages, browser reads via SSE.
 - Machine daemon: `ak start` — poll loop, auto-claim todo tasks, spawn agent CLI per task. PID lock, graceful shutdown, exponential backoff. `processManager.ts` handles spawn/monitor/kill/chat relay.
-- Repo linking: `ak link` registers repo at tenant level and maps local directory to repository ID. Stored in `~/.agent-kanban/links.json`.
+- Repo management: `ak create repo` registers repo at tenant level. `ak get repo` lists registered repos.
 - Data model: Board is the workspace unit. Repositories belong to owner (tenant-level, like machines). Tasks belong to boards, optionally linked to a repository. Machines belong to owner (user/org).
 
 ## Post-Write Workflow
diff --git a/skills/agent-kanban/SKILL.md b/skills/agent-kanban/SKILL.md
@@ -11,19 +11,47 @@ You are a worker agent. Use the `ak` CLI to work on your assigned task.
 ## Your Workflow
 
 1. **Claim** your assigned task → `ak task claim <id>`
-2. **Log** progress as you work → `ak task log <id> "doing X..."`
+2. **Log** progress as you work → `ak create note --task <id> "doing X..."`
 3. **Submit for review** when done → `ak task review <id> --pr-url <url>`
 
-## Commands You Need
+## Commands
+
+### Task Lifecycle
 
 | Command | Description |
 |---------|-------------|
-| `ak task claim <id>` | Claim your assigned task → starts work (in_progress) |
-| `ak task log <id> <message>` | Add a progress log entry |
-| `ak task review <id>` | Submit for review (--pr-url to attach PR) |
-| `ak task complete <id>` | Complete task (--result, --pr-url) |
-| `ak task view <id>` | View task details (description, input, deps) |
-| `ak task list` | List tasks (--status, --label, --repo) |
+| `ak task claim <id>` | Claim your assigned task (in_progress) |
+| `ak task review <id> --pr-url <url>` | Submit task for review with PR link |
+| `ak task cancel <id>` | Cancel a task |
+| `ak task reject <id> --reason "..."` | Reject task from review back to in_progress |
+
+### Resource CRUD (kubectl-style)
+
+| Command | Description |
+|---------|-------------|
+| `ak get task [id]` | View task details, or list tasks with filters |
+| `ak get task --board <id> --status <s>` | List tasks filtered by board, status, label, repo |
+| `ak get note --task <id>` | View progress logs for a task |
+| `ak create note --task <id> "message"` | Add a progress log entry |
+| `ak create task --board <id> --title "..."` | Create a new task |
+| `ak get agent` | List agents |
+| `ak get agent --format json` | List agents as JSON |
+| `ak get board` | List boards |
+| `ak get repo` | List repositories |
+| `ak create repo --name "..." --url "..."` | Register a repository |
+
+### Create Task Options
+
+```
+ak create task --board <id> --title "Title" \
+  --description "Details" \
+  --repo <repo-id> \
+  --priority medium \
+  --labels "bug,frontend" \
+  --assign-to <agent-id> \
+  --parent <task-id> \
+  --depends-on "id1,id2"
+```
 
 ## Output Format
 
@@ -32,6 +60,9 @@ You are a worker agent. Use the `ak` CLI to work on your assigned task.
 ## Rules
 
 - **If claim fails, stop immediately** — do not write any code or make any changes. Report the error and wait.
+- **Never call `task complete`** — only humans complete tasks.
+- Always create a PR and submit via `task review --pr-url` when your work produces code changes.
+- Log progress frequently — humans monitor the board.
 
 ## Error Handling
 
PATCH

echo "Gold patch applied."
