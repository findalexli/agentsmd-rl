#!/usr/bin/env bash
set -euo pipefail

cd /workspace/core

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md

diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1 @@
-.github/copilot-instructions.md
\ No newline at end of file
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
