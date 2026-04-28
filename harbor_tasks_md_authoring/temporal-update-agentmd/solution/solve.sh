#!/usr/bin/env bash
set -euo pipefail

cd /workspace/temporal

# Idempotency guard
if grep -qF "- Prefer `require` over `assert`, avoid testify suites in unit tests (functional" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -75,6 +75,7 @@ Before starting the implementation of any request, you MUST REVIEW the following
 - Write tests for new functionality
 - Run tests after altering code or tests
 - Start with unit tests for fastest feedback
+- Prefer `require` over `assert`, avoid testify suites in unit tests (functional tests require suites for test cluster setup), use `require.Eventually` instead of `time.Sleep` (forbidden by linter)
 
 # Primary Workflows
 ## Software Engineering Tasks
PATCH

echo "Gold patch applied."
