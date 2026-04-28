#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flood

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1 @@
-AGENTS.md
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
