#!/usr/bin/env bash
set -euo pipefail

cd /workspace/egregore

# Idempotency guard
if grep -qF "**Local mode** (`mode === \"local\"`): Skip ALL `bin/graph.sh` calls \u2014 do NOT run " ".claude/skills/add/SKILL.md" && grep -qF "- **Create mode**: Step 0 context capture \u2014 run Bash call 1 (git identity + stat" ".claude/skills/issue/SKILL.md" && grep -qF "- **Add**: Ensure directory and file exist (see initialization above). Parse tex" ".claude/skills/todo/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add/SKILL.md b/.claude/skills/add/SKILL.md
@@ -12,15 +12,31 @@ Arguments: $ARGUMENTS (Optional: URL to fetch, or leave empty for interactive mo
 - `/add` — Interactive mode, prompts for content
 - `/add [url]` — Fetch and ingest external source
 
+## Mode detection
+
+```bash
+MODE=$(jq -r '.mode // "connected"' egregore.json 2>/dev/null)
+```
+
+**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).
+
+Local-mode flow:
+- Steps 1-5 (fetch, type, quests, topics, file creation) work normally — quest matching reads from `memory/quests/` directory instead of graph query.
+- Step 6 (Neo4j Artifact node): skip entirely. The artifact file in `memory/artifacts/` is the source of truth.
+- Step 7: confirm file saved, skip relation messaging. Show `✓ Saved to memory/artifacts/{filename}`.
+- Auto-save (commit + push) works normally.
+
+**Connected mode**: Full behavior including graph nodes as specified below.
+
 ## What to do
 
 1. If URL provided, fetch and extract content
 2. Ask for or infer content type
-3. Suggest relevant quests based on content
+3. Suggest relevant quests based on content (local mode: read from `memory/quests/` files)
 4. Suggest topics
 5. Create artifact file with proper frontmatter
-6. Create Artifact node in Neo4j via `bash bin/graph.sh query "..."` (never MCP, suppress raw output — capture in variable, only show status)
-7. Confirm relations created
+6. Create Artifact node in Neo4j via `bash bin/graph.sh query "..."` (never MCP, suppress raw output — capture in variable, only show status) — **CONNECTED MODE ONLY**
+7. Confirm relations created (local mode: confirm file saved only)
 
 ## Artifact types
 
diff --git a/.claude/skills/issue/SKILL.md b/.claude/skills/issue/SKILL.md
@@ -9,6 +9,23 @@ Topic: $ARGUMENTS
 
 **Auto-saves.** No need to run `/save` after (create mode only).
 
+## Mode detection
+
+```bash
+MODE=$(jq -r '.mode // "connected"' egregore.json 2>/dev/null)
+```
+
+**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` and `bin/notify.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).
+
+Local-mode flow:
+- **Create mode**: Step 0 context capture — run Bash call 1 (git identity + state) normally; skip Bash call 2's `bin/graph.sh test` line (keep the memory-symlink and egregore.json checks); skip the Neo4j recent-session query entirely. Steps 1-2 (description, smart routing) work normally. Step 3 — write the markdown file to `memory/knowledge/issues/` normally, but skip the Neo4j `CREATE (i:Issue)` node and the progress message referencing "graph". Skip Step 4 graph routing updates entirely. Skip Step 5 notifications entirely. Steps 6-7 (auto-save, confirmation TUI) work normally — in the TUI, show `✓ Saved to memory` (omit "graphed" and "team notified").
+- **List mode**: Read issues from `memory/knowledge/issues/` directory — parse frontmatter for id, title, status, recipient, created, topics. Render same TUI.
+- **Close mode**: Find issue file in `memory/knowledge/issues/`, update frontmatter `status: closed` + add `closed: {date}`. Skip graph update.
+- **Search mode**: Grep through `memory/knowledge/issues/` files for matching text. Render same TUI.
+- **Notifications**: Skip entirely — do not mention notifications.
+
+**Connected mode**: Full behavior including graph nodes and notifications as specified below.
+
 ## Execution rules
 
 **Neo4j-first.** All queries via `bash bin/graph.sh query "..."`. No MCP. No direct curl to Neo4j.
diff --git a/.claude/skills/todo/SKILL.md b/.claude/skills/todo/SKILL.md
@@ -18,6 +18,66 @@ Arguments: $ARGUMENTS (Optional: text to add, "done N", "cancel N", quest slug,
 - `/todo [quest-slug]` — Quest-scoped view
 - `/todo all` — Include done/cancelled (14 days)
 
+## Step 0: Mode detection
+
+```bash
+MODE=$(jq -r '.mode // "connected"' egregore.json 2>/dev/null)
+```
+
+**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).
+
+Local-mode storage: `memory/todos/{person}.md` — a YAML-frontmatter markdown file per user.
+
+Local-mode flow:
+- **All routes** (add, list, done, cancel, check): same UX and TUI rendering, backed by YAML parse/write instead of Cypher queries.
+- **Quest matching**: check `memory/quests/` directory for active quest files instead of graph query.
+- **Person detection**: check `memory/people/` directory for person files instead of graph query.
+- **CheckIn persistence**: not available in local mode (no graph storage). The check-in flow still works interactively but check-in history is not persisted.
+- **Notifications**: skip entirely — do not mention notifications.
+
+### Local-mode file format
+
+File: `memory/todos/{person}.md`
+
+```yaml
+---
+todos:
+  - id: "2026-03-30-bartu-001"
+    text: "review bugs manually"
+    status: open
+    priority: 0
+    created: "2026-03-30T22:00:00Z"
+    completed: null
+    quest: null
+    source: manual
+    blockedBy: null
+    deferredUntil: null
+    lastNote: null
+    lastTransition: null
+---
+```
+
+### Local-mode initialization
+
+On first use, the directory and file may not exist. Before any read or write:
+1. `mkdir -p memory/todos/`
+2. If `memory/todos/{person}.md` does not exist, create it with:
+   ```yaml
+   ---
+   todos: []
+   ---
+   ```
+
+### Local-mode route adjustments
+
+- **Add**: Ensure directory and file exist (see initialization above). Parse text, determine priority, check `memory/quests/` for quest matching (read frontmatter `status: active` from quest files). Generate todo ID as `YYYY-MM-DD-{person}-{NNN}` where NNN is zero-padded 3 digits: count existing entries in the `todos` array whose `id` starts with today's `YYYY-MM-DD-{person}-` prefix, add 1 (e.g., if 2 exist for today, next is `003`). Append to the YAML `todos` array. Write file.
+- **List**: Read the YAML file, filter by status, sort by priority desc then created desc. Render same TUI.
+- **Done/Cancel**: Read file, filter to active items (status `open`, `blocked`, `deferred`), sort by priority desc then created desc (same order as List display). Positional references (e.g., `todo done 2`) resolve against this filtered+sorted list — position 2 means the 2nd displayed item, not the 2nd entry in the raw YAML array. For text match, search the `text` field of filtered items. Update matched item's status + `completed` timestamp in the YAML. Write file.
+- **Check**: Read file, filter active items, walk through with AskUserQuestion (same UX). Update statuses in YAML after each item. Skip CheckIn node creation.
+- **Quest view**: Read file, filter todos where `quest` matches the slug. Same TUI with quest header.
+
+**Connected mode**: Full behavior including graph nodes and notifications as specified below.
+
 ## Step 1: Get Current User
 
 ```bash
@@ -553,7 +613,8 @@ Output:
 
 | Scenario | Handling |
 |----------|----------|
-| Neo4j unavailable | "Graph offline — todos need the knowledge graph. Try again when connected." |
+| Neo4j unavailable (connected mode) | Still attempt file-based save. Show warning: "Graph offline — file saved, will sync on next /save" |
+| Local mode | Skip all graph calls silently — no warnings, no "graph offline" messaging. YAML file is the source of truth. TUI renders identically. |
 | No open todos (list) | "No open todos. /todo [text] to add one." |
 | Text matches multiple (done/cancel) | Show matches, AskUserQuestion to pick |
 | Person not in graph (mention) | Save todo without MENTIONS. Warn: "[name] not found in graph." |
PATCH

echo "Gold patch applied."
