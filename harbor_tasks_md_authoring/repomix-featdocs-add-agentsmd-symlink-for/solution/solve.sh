#!/usr/bin/env bash
set -euo pipefail

cd /workspace/repomix

# Idempotency guard
if grep -qF ".agents/rules/base.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+.agents/rules/base.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
