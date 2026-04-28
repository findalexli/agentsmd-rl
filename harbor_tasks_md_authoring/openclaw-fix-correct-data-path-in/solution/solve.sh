#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency guard
if grep -qF "8. **NEVER start Codex in ~/.openclaw/** - it'll read your soul docs and get wei" "skills/coding-agent/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/coding-agent/SKILL.md b/skills/coding-agent/SKILL.md
@@ -231,7 +231,7 @@ git worktree remove /tmp/issue-99
 5. **--full-auto for building** - auto-approves changes
 6. **vanilla for reviewing** - no special flags needed
 7. **Parallel is OK** - run many Codex processes at once for batch work
-8. **NEVER start Codex in ~/clawd/** - it'll read your soul docs and get weird ideas about the org chart!
+8. **NEVER start Codex in ~/.openclaw/** - it'll read your soul docs and get weird ideas about the org chart!
 9. **NEVER checkout branches in ~/Projects/openclaw/** - that's the LIVE OpenClaw instance!
 
 ---
PATCH

echo "Gold patch applied."
