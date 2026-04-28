#!/usr/bin/env bash
set -euo pipefail

cd /workspace/core

# Idempotency guard
if grep -qF "For advanced configurations (Event Listeners, MongoDB, Behat tuning), refer to `" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -26,7 +26,7 @@ When to use:
 
 3. Testing Quick-Reference (Default/Symfony)
 
-For advanced configurations (Event Listeners, MongoDB, Behat tuning), refer to `tests/GEMINI.md`.
+For advanced configurations (Event Listeners, MongoDB, Behat tuning), refer to `tests/AGENTS.md`.
 
 Common Commands:
 
PATCH

echo "Gold patch applied."
