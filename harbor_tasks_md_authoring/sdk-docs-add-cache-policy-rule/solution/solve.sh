#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sdk

# Idempotency guard
if grep -qF "- Video/image generation costs real money ($0.05\u2013$0.50+ per generation) and take" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -123,3 +123,13 @@ bun --hot ./index.ts
 ```
 
 For more information, read the Bun API docs in `node_modules/bun-types/docs/**.md`.
+
+## Cache Policy
+
+**NEVER clear or delete the user's cache**, even when debugging.
+
+- Video/image generation costs real money ($0.05–$0.50+ per generation) and takes 60–180 seconds
+- The cache is the user's asset — treat it as production data, not disposable debug state
+- If you need to regenerate, modify the prompt slightly or use a different cache key
+- If cache must be cleared, always ask the user explicitly first
+- Suggest `--no-cache` flag for one-off re-renders instead of deleting cached files
PATCH

echo "Gold patch applied."
