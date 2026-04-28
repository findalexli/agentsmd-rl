#!/usr/bin/env bash
set -euo pipefail

cd /workspace/orb-software

# Idempotency guard
if grep -qF "Note: If @AGENTS.override.md exists,treat it as the ultimate source of truth for" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,5 +1,5 @@
-Note: If ./AGENTS.override.md exists,treat it as the ultimate source of truth for AGENTS.md.
-If there are any differences between AGENTS.md and AGENTS.override.md, the latter takes precedence.
+Note: If @AGENTS.override.md exists,treat it as the ultimate source of truth for AGENTS.md and read it right now.
+If there are any differences between this file and AGENTS.override.md, the latter takes precedence.
 
 # Repository Guidelines
 
PATCH

echo "Gold patch applied."
