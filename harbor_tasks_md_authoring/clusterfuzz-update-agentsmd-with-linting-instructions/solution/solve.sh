#!/usr/bin/env bash
set -euo pipefail

cd /workspace/clusterfuzz

# Idempotency guard
if grep -qF "It's possible to get into a state where linting and formatting contradict each o" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -92,3 +92,4 @@ python butler.py format
 ```
 
 This will format the changed code in your current branch.
+It's possible to get into a state where linting and formatting contradict each other. In this case, STOP, the human will fix it.
PATCH

echo "Gold patch applied."
