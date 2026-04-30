#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backstage

# Idempotency guard
if grep -qF "Follow the instructions at /.github/copilot-instructions.md" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1 @@
+Follow the instructions at /.github/copilot-instructions.md
PATCH

echo "Gold patch applied."
