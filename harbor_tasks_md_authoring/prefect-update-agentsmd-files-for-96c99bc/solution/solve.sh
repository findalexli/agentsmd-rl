#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **Retrying HTTP requests** (`hosted_api_client` tests): SQLite \"database is lo" "tests/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tests/AGENTS.md b/tests/AGENTS.md
@@ -41,7 +41,15 @@ Shared fixtures live in `fixtures/` (see fixtures/AGENTS.md) and root `conftest.
 ### Flaky Tests
 We have a workflow that identifies and fixes tests that flake after merging to main. Check CI test output to see which tests are currently slow or flaky.
 
-For tests using `hosted_api_client` (which spins up a real subprocess server), SQLite "database is locked" 503 errors can occur due to concurrent access between the test session and the server subprocess. Use `retry_asserts` from `prefect._internal.testing` to retry the HTTP request portion only — keep the result assertions outside the retry loop so a wrong result is never masked.
+Use `retry_asserts` from `prefect._internal.testing` to handle timing-sensitive assertions. Two patterns:
+
+- **Retrying assertions for async event propagation** (most common): wrap the assertion inside `with attempt:` so it retries until the event arrives.
+  ```python
+  async for attempt in retry_asserts(max_attempts=5, delay=0.5):
+      with attempt:
+          callback.assert_called_once_with(flow_run_id)
+  ```
+- **Retrying HTTP requests** (`hosted_api_client` tests): SQLite "database is locked" 503 errors can occur due to concurrent access. Retry the HTTP request inside the loop; keep the result assertions *outside* so a wrong result is never masked.
 
 ## Related
 
PATCH

echo "Gold patch applied."
