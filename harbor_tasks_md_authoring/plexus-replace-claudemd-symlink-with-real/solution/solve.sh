#!/usr/bin/env bash
set -euo pipefail

cd /workspace/plexus

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "See AGENTS.md for project instructions and guidelines." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +0,0 @@
-AGENTS.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+See AGENTS.md for project instructions and guidelines.
PATCH

echo "Gold patch applied."
