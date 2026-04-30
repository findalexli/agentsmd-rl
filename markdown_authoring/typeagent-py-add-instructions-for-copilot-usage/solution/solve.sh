#!/usr/bin/env bash
set -euo pipefail

cd /workspace/typeagent-py

# Idempotency guard
if grep -qF "Get your instructions from AGENTS.md in the repo root." ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1 @@
+Get your instructions from AGENTS.md in the repo root.
PATCH

echo "Gold patch applied."
