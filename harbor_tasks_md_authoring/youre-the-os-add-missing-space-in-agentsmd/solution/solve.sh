#!/usr/bin/env bash
set -euo pipefail

cd /workspace/youre-the-os

# Idempotency guard
if grep -qF "* Do not make breaking changes to the [automation API](automation/api.py) unless" "agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agents.md b/agents.md
@@ -40,4 +40,4 @@
 ## Coding Restrictions
 
 * Use the "Open-closed principle" as a loose guideline. As such, try to avoid solutions that alter existing implementations or interfaces. If such changes appear to be unavoidable, discuss them with the user first.
-* Do not make breaking changes to the [automation API](automation/api.py)unless explicitly instructed to.
+* Do not make breaking changes to the [automation API](automation/api.py) unless explicitly instructed to.
PATCH

echo "Gold patch applied."
