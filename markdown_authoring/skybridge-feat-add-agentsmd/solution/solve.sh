#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skybridge

# Idempotency guard
if grep -qF "When the public API of `packages/core/` changes, verify that `skills/chatgpt-app" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,3 @@
+# PR Reviewer Instructions
+
+When the public API of `packages/core/` changes, verify that `skills/chatgpt-app-builder/` and `docs/` are updated to match.
PATCH

echo "Gold patch applied."
