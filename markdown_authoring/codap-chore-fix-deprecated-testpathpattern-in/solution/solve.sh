#!/usr/bin/env bash
set -euo pipefail

cd /workspace/codap

# Idempotency guard
if grep -qF "# Run tests matching a pattern (pass the pattern directly, NOT via --testPathPat" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -129,8 +129,8 @@ npm test
 # Run a specific test file
 npm test -- path/to/file.test.ts
 
-# Run tests matching a pattern
-npm test -- --testPathPattern="data-set"
+# Run tests matching a pattern (pass the pattern directly, NOT via --testPathPattern which is deprecated)
+npm test -- data-set
 
 # Run tests in watch mode
 npm run test:watch
PATCH

echo "Gold patch applied."
