#!/bin/bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-/workspace/react}"
BUGGY_FILE="packages/react-devtools-shared/src/backend/fiber/renderer.js"

# Check if fix already applied (idempotency check)
# The bug: Map.set(firstInstance, nearestInstance) wrong order
# The fix: Map.set(publicInstance, firstInstance)
if grep -q "firstInstance,\s*$" "$REPO_DIR/$BUGGY_FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

# Apply the gold patch
git -C "$REPO_DIR" apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 3214c8392285..916d69823285 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -991,8 +991,8 @@ function releaseHostResource(
         // eslint-disable-next-line no-for-of-loops/no-for-of-loops
         for (const firstInstance of resourceInstances) {
           publicInstanceToDevToolsInstanceMap.set(
+            publicInstance,
             firstInstance,
-            nearestInstance,
           );
           break;
         }
PATCH

echo "Fix applied successfully."
