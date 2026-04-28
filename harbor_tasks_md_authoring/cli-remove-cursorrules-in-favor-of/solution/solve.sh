#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF ".cursorrules" ".cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -1 +0,0 @@
-AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
