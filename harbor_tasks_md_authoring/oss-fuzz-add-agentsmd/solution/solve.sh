#!/usr/bin/env bash
set -euo pipefail

cd /workspace/oss-fuzz

# Idempotency guard
if grep -qF "* If doing development on infra/ you should use a venv and if it doesn't already" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,3 @@
+* Use python3 infra/helper.py to build projects and run fuzzers.
+* If doing development on infra/ you should use a venv and if it doesn't already exist, install deps from infra/ci/requirements.txt build/functions/requirements.txt with pip.
+* If doing development on infra/ run python infra/presubmit.py to format, lint and run tests.
PATCH

echo "Gold patch applied."
