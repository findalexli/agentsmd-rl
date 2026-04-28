#!/usr/bin/env bash
set -euo pipefail

cd /workspace/archsmith

# Idempotency guard
if grep -qF "- Do NOT append `Co-Authored-By` lines to commit messages." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,5 @@
+# AGENTS.md
+
+## Git Commit Rules
+
+- Do NOT append `Co-Authored-By` lines to commit messages.
PATCH

echo "Gold patch applied."
