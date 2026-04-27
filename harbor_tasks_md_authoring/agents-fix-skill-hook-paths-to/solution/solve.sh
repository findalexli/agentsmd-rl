#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "**Important:** Hooks in `SKILL.md` frontmatter can use **relative paths** from t" "AGENTS.md" && grep -qF "command: \"uv run ./scripts/cli.py ensure\"" "skills/analyzing-data/SKILL.md" && grep -qF "command: \"uv run ../analyzing-data/scripts/cli.py ensure\"" "skills/init/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -72,11 +72,13 @@ Everything is defined inline in `.claude-plugin/marketplace.json` following the
 
 Use `${CLAUDE_PLUGIN_ROOT}` to reference files within the plugin (required because plugins are copied to a cache location when installed).
 
+**Important:** Hooks in `SKILL.md` frontmatter can use **relative paths** from the skill's directory (e.g., `./scripts/bar.py`). Use `${CLAUDE_PLUGIN_ROOT}` in `marketplace.json` to reference the plugin root.
+
 ## Key Files
 
 - `.claude-plugin/marketplace.json` - Marketplace catalog with inline plugin definition (hooks, mcpServers)
 - `skills/*/SKILL.md` - Individual skills (auto-discovered)
-- `skills/*/hooks/*.sh` - Hook scripts (co-located with skills, referenced via `${CLAUDE_PLUGIN_ROOT}/skills/<name>/hooks/...`)
+- `skills/*/hooks/*.sh` - Hook scripts (co-located with skills, referenced via relative paths from SKILL.md or `${CLAUDE_PLUGIN_ROOT}/skills/<name>/hooks/...` from marketplace.json)
 
 ## Config Location
 
diff --git a/skills/analyzing-data/SKILL.md b/skills/analyzing-data/SKILL.md
@@ -6,12 +6,12 @@ hooks:
     - matcher: "Bash"
       hooks:
         - type: command
-          command: "uv run ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-data/scripts/cli.py ensure"
+          command: "uv run ./scripts/cli.py ensure"
           once: true
   Stop:
     - hooks:
         - type: command
-          command: "uv run ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-data/scripts/cli.py stop"
+          command: "uv run ./scripts/cli.py stop"
 ---
 
 # Data Analysis
diff --git a/skills/init/SKILL.md b/skills/init/SKILL.md
@@ -6,19 +6,19 @@ hooks:
     - matcher: "Bash"
       hooks:
         - type: command
-          command: "uv run ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-data/scripts/cli.py ensure"
+          command: "uv run ../analyzing-data/scripts/cli.py ensure"
           once: true
   Stop:
     - hooks:
         - type: command
-          command: "uv run ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-data/scripts/cli.py stop"
+          command: "uv run ../analyzing-data/scripts/cli.py stop"
 ---
 
 # Initialize Warehouse Schema
 
 Generate a comprehensive, user-editable schema reference file for the data warehouse.
 
-**Scripts:** `$CLAUDE_PLUGIN_ROOT/skills/analyzing-data/scripts/`
+**Scripts:** `../analyzing-data/scripts/`
 
 ## What This Does
 
PATCH

echo "Gold patch applied."
