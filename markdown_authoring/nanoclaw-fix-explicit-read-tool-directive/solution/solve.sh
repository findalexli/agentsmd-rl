#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "1. Use the Read tool to read `.claude/skills/setup/diagnostics.md`." ".claude/skills/setup/SKILL.md" && grep -qF "1. Use the Read tool to read `.claude/skills/update-nanoclaw/diagnostics.md`." ".claude/skills/update-nanoclaw/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -287,4 +287,5 @@ Tell user to test: send a message in their registered chat. Show: `tail -f logs/
 
 ## 9. Diagnostics
 
-Send diagnostics data by following `.claude/skills/setup/diagnostics.md`.
+1. Use the Read tool to read `.claude/skills/setup/diagnostics.md`.
+2. Follow every step in that file before completing setup.
diff --git a/.claude/skills/update-nanoclaw/SKILL.md b/.claude/skills/update-nanoclaw/SKILL.md
@@ -237,4 +237,5 @@ Tell the user:
 
 ## Diagnostics
 
-Send diagnostics data by following `.claude/skills/update-nanoclaw/diagnostics.md`.
+1. Use the Read tool to read `.claude/skills/update-nanoclaw/diagnostics.md`.
+2. Follow every step in that file before finishing.
PATCH

echo "Gold patch applied."
