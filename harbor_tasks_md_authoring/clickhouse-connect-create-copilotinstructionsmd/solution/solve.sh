#!/usr/bin/env bash
set -euo pipefail

cd /workspace/clickhouse-connect

# Idempotency guard
if grep -qF "Use the review instructions in .agents/review.md" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1 @@
+Use the review instructions in .agents/review.md
PATCH

echo "Gold patch applied."
