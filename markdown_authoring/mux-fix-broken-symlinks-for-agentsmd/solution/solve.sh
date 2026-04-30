#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mux

# Idempotency guard
if grep -qF "docs/AGENTS.md" "AGENTS.md" && grep -qF "docs/AGENTS.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1 +1 @@
-docs/src/AGENTS.md
\ No newline at end of file
+docs/AGENTS.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1 @@
-docs/src/AGENTS.md
\ No newline at end of file
+docs/AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
