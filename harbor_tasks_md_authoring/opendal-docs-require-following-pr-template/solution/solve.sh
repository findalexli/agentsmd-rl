#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opendal

# Idempotency guard
if grep -qF "- Always follow OpenDAL's pull request template when creating a PR." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -149,6 +149,9 @@ ci: Update GitHub Actions workflow
 refactor(core): Simplify error handling
 ```
 
+## Pull Request Requirements
+- Always follow OpenDAL's pull request template when creating a PR.
+
 ## Testing Approach
 - Unit tests in `src/tests/`
 - Behavior tests validate service implementations
PATCH

echo "Gold patch applied."
