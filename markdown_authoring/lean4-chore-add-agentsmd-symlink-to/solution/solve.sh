#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lean4

# Idempotency guard
if grep -qF ".claude/CLAUDE.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+.claude/CLAUDE.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
