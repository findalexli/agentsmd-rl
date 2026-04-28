#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency guard
if grep -qF "../.github/copilot-instructions.md" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1 @@
+../.github/copilot-instructions.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
