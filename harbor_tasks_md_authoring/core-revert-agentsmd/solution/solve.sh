#!/usr/bin/env bash
set -euo pipefail

cd /workspace/core

# Idempotency guard
if grep -qF ".github/copilot-instructions.md" ".github/copilot-instructions.md" && grep -qF ".github/copilot-instructions.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md

diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1 @@
-AGENTS.md
\ No newline at end of file
+.github/copilot-instructions.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
