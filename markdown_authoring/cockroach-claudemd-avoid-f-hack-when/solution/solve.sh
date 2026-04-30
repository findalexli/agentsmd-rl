#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cockroach

# Idempotency guard
if grep -qF "# Build the tests in package ./pkg/util/log" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -15,11 +15,10 @@ preferred to direct `go (build|test)` or `bazel` invocations.
 This is useful as a compilation check.
 
 ```bash
-# Invoke (but skip) all tests in that package, which
-# implies that both package and its tests compile.
-./dev test ./pkg/util/log -f -.
 # Build package ./pkg/util/log
-./dev build ./pkg/util/log
+./dev build pkg/util/log
+# Build the tests in package ./pkg/util/log
+./dev build pkg/util/log:log_test
 ```
 
 **Testing:**
PATCH

echo "Gold patch applied."
