#!/usr/bin/env bash
set -euo pipefail

cd /workspace/oh-my-opencode-slim

# Idempotency guard
if grep -qF "**OpenCode auto-loads `AGENTS.md` into agent context on every session.** To ensu" "src/skills/cartography/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/skills/cartography/SKILL.md b/src/skills/cartography/SKILL.md
@@ -79,6 +79,29 @@ Once all specific directories are mapped, the Orchestrator must create or update
 2.  **Aggregate Sub-Maps**: Create a "Repository Directory Map" section. For every folder that has a `codemap.md`, extract its **Responsibility** summary and include it in a table or list in the root map.
 3.  **Cross-Reference**: Ensure that the root map contains the absolute or relative paths to the sub-maps so agents can jump directly to the relevant details.
 
+### Step 5: Register Codemap in AGENTS.md
+
+**OpenCode auto-loads `AGENTS.md` into agent context on every session.** To ensure agents automatically discover and use the codemap, update (or create) `AGENTS.md` at the repo root:
+
+1. If `AGENTS.md` already exists and already contains a `## Repository Map` section, **skip this step** — the reference is already set up.
+2. If `AGENTS.md` exists but has no `## Repository Map` section, **append** the section below.
+3. If `AGENTS.md` doesn't exist, **create** it with the section below.
+
+```markdown
+## Repository Map
+
+A full codemap is available at `codemap.md` in the project root.
+
+Before working on any task, read `codemap.md` to understand:
+- Project architecture and entry points
+- Directory responsibilities and design patterns
+- Data flow and integration points between modules
+
+For deep work on a specific folder, also read that folder's `codemap.md`.
+```
+
+This is idempotent — repeated cartography runs will detect the existing section and skip. No duplication.
+
 
 ## Codemap Content
 
PATCH

echo "Gold patch applied."
