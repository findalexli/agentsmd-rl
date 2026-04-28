#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shardingsphere

# Idempotency guard
if grep -qF "- Clean context after codes committed." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -139,3 +139,4 @@ Key directories and their purposes:
   - Verify rule compliance after each user interaction.
   - Report violations through clear error messages.
   - Use Spotless to enforce code style after code generated.
+  - Clean context after codes committed.
PATCH

echo "Gold patch applied."
