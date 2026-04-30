#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opensre

# Idempotency guard
if grep -qF "raise FileNotFoundError(f\"input file not present: {input_path}\")" "tests/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tests/AGENTS.md b/tests/AGENTS.md
@@ -10,7 +10,7 @@
 # use_case.py - Pure business logic, no test infrastructure
 def extract_and_validate(input_path: str) -> str:
     if not os.path.exists(input_path):
-        raise FileNotFoundError(f"empty file not present: {input_path}")
+        raise FileNotFoundError(f"input file not present: {input_path}")
     return data
 
 # test_orchestrator.py - All test orchestration separate
PATCH

echo "Gold patch applied."
