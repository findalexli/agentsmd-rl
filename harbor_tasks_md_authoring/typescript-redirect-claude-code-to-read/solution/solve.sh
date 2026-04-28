#!/usr/bin/env bash
set -euo pipefail

cd /workspace/typescript

# Idempotency guard
if grep -qF "Read AGENTS.md before proceeding." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+Read AGENTS.md before proceeding.
\ No newline at end of file
PATCH

echo "Gold patch applied."
