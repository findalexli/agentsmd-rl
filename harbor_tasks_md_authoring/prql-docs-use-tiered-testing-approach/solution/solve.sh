#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotency guard
if grep -qF "Use a tiered testing approach\u2014iterate quickly, validate thoroughly:" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,26 +2,30 @@
 
 ## Development Workflow
 
-Use a tight inner loop for fast feedback, comprehensive outer loop before
-returning to user:
+Use a tiered testing approach—iterate quickly, validate thoroughly:
 
-**Inner loop** (fast, focused, <5s):
+**Inner loop** (during development, ~5s):
 
 ```sh
-# Run fast tests on core packages (from project root)
+# Fast tests on core packages
 task prqlc:test
 
-# Unit tests filtered by test name
+# Filtered by test name
 cargo insta test -p prqlc --lib -- resolver
-
-# Integration tests filtered by test name
 cargo insta test -p prqlc --test integration -- date
 ```
 
-**Outer loop** (comprehensive, ~1min, before returning to user):
+**Before returning to user** (~30s):
+
+```sh
+# Comprehensive prqlc tests - sufficient for most changes
+task prqlc:pull-request
+```
+
+**Cross-binding changes only** (~2min):
 
 ```sh
-# Run everything - this is required before returning
+# Only when changes affect JS/Python/wasm bindings
 task test-all
 ```
 
PATCH

echo "Gold patch applied."
