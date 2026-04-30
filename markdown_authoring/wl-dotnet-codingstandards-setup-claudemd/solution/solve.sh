#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wl-dotnet-codingstandards

# Idempotency guard
if grep -qF "../CLAUDE.md" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1 +1 @@
-CLAUDE.md
\ No newline at end of file
+../CLAUDE.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
