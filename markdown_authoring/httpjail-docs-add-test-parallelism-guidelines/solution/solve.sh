#!/usr/bin/env bash
set -euo pipefail

cd /workspace/httpjail

# Idempotency guard
if grep -qF "**Integration tests should run in parallel by default.** The jails are designed " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -59,6 +59,16 @@ cargo test
 
 This ensures fast feedback during development and prevents CI timeouts.
 
+### Test Parallelism
+
+**Integration tests should run in parallel by default.** The jails are designed to be independent from each other, so the test suite should leverage good parallelism. Tests should only be marked as serial (`#[serial]`) when there's a specific global resource that would be contended, such as:
+
+- Global system settings that affect all processes
+- Shared network ports or interfaces
+- System-wide firewall rules that can't be isolated
+
+Each jail operates in its own network namespace (on Linux) or with its own proxy port, so most tests can safely run concurrently. This significantly reduces total test runtime.
+
 ## Cargo Cache
 
 Occasionally you will encounter permissions issues due to running the tests under sudo. In these cases,
PATCH

echo "Gold patch applied."
