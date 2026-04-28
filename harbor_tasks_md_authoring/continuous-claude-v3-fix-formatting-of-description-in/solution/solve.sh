#!/usr/bin/env bash
set -euo pipefail

cd /workspace/continuous-claude-v3

# Idempotency guard
if grep -qF "description: \"Completion Check: Verify Infrastructure Is Wired\"" ".claude/skills/completion-check/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/completion-check/SKILL.md b/.claude/skills/completion-check/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: completion-check
-description: Completion Check: Verify Infrastructure Is Wired
+description: "Completion Check: Verify Infrastructure Is Wired"
 user-invocable: false
 ---
 
PATCH

echo "Gold patch applied."
