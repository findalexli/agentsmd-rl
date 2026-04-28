#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ethical-ad-server

# Idempotency guard
if grep -qF "The full test suite takes a couple of minutes to run." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -38,6 +38,7 @@ Imports should go at the top of the file, after any docstrings unless there is a
 ## 3. Testing Procedures
 
 Run `tox` to run the test suite.
+The full test suite takes a couple of minutes to run.
 This verifies the code style and linting and runs the full test suite.
 The test suite verifies that there are no missing migrations
 and that test coverage is above the threshold defined in `pyproject.toml`.
PATCH

echo "Gold patch applied."
