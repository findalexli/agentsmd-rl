#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aidd

# Idempotency guard
if grep -qF "globs: **/*.js,**/*.jsx,**/*.ts,**/*.tsx" "ai/js-and-typescript.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ai/js-and-typescript.mdc b/ai/js-and-typescript.mdc
@@ -1,7 +1,7 @@
 ---
 description: Style guide and best practices for writing JavaScript and TypeScript code
-globs: "**/*.js,**/*.jsx,**/*.ts,**/*.tsx"
-alwaysApply: true
+globs: **/*.js,**/*.jsx,**/*.ts,**/*.tsx
+alwaysApply: false
 ---
 
 # JavaScript/TypeScript guide
PATCH

echo "Gold patch applied."
