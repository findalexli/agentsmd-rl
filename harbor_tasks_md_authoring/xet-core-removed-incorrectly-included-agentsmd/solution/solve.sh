#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xet-core

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1 +0,0 @@
-../../resources/AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
