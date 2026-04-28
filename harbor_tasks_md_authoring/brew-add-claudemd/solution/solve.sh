#!/usr/bin/env bash
set -euo pipefail

cd /workspace/brew

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
PATCH

echo "Gold patch applied."
