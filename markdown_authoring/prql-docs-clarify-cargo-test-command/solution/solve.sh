#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotency guard
if grep -qF "cargo insta test -p prqlc --test integration -- date" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -11,11 +11,11 @@ returning to user:
 # Run fast tests on core packages (from project root)
 task prqlc:test
 
-# Or run specific tests you're working on
-cargo insta test -p prqlc --test integration -- date
+# Unit tests filtered by test name
+cargo insta test -p prqlc --lib -- resolver
 
-# Run unit tests for a specific module
-cargo insta test -p prqlc --lib semantic::resolver
+# Integration tests filtered by test name
+cargo insta test -p prqlc --test integration -- date
 ```
 
 **Outer loop** (comprehensive, ~1min, before returning to user):
PATCH

echo "Gold patch applied."
