#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fundamental-ngx

# Idempotency guard
if grep -qF "Read and follow AGENTS.md for all development conventions." ".cursorrules" && grep -qF "Read and follow AGENTS.md for all development conventions." ".windsurfrules" && grep -qF "Read and follow AGENTS.md for all development conventions." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -0,0 +1 @@
+Read and follow AGENTS.md for all development conventions.
diff --git a/.windsurfrules b/.windsurfrules
@@ -0,0 +1 @@
+Read and follow AGENTS.md for all development conventions.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+Read and follow AGENTS.md for all development conventions.
PATCH

echo "Gold patch applied."
