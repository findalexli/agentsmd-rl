#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gumroad

# Idempotency guard
if grep -qF "@CONTRIBUTING.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+@CONTRIBUTING.md
PATCH

echo "Gold patch applied."
