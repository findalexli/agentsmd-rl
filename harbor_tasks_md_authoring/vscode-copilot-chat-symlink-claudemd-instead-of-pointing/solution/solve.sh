#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode-copilot-chat

# Idempotency guard
if grep -qF ".claude/CLAUDE.md" ".claude/CLAUDE.md" && grep -qF "../.github/copilot-instructions.md" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -1,7 +0,0 @@
-# Claude Instructions
-
-## General Repository Instructions
-
-For all repository instructions, coding standards, and development guidelines, **ALWAYS** read:
-
-**[.github/copilot-instructions.md](../.github/copilot-instructions.md)**
\ No newline at end of file
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1 @@
+../.github/copilot-instructions.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
