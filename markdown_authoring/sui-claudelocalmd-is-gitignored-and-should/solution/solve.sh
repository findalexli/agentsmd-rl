#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sui

# Idempotency guard
if grep -qF "CLAUDE.local.md" "CLAUDE.local.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.local.md b/CLAUDE.local.md
@@ -1 +0,0 @@
-# Contains user-specific overrides to CLAUDE.md. Do not commit changes to this file.
\ No newline at end of file
PATCH

echo "Gold patch applied."
