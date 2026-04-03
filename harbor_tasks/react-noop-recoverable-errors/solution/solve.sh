#!/bin/bash
set -euo pipefail

cd /workspace/react
# Check if already applied (look for the eslint-disable comment added in the fix)
if grep -q "react-internal/no-production-logging" packages/react-noop-renderer/src/createReactNoop.js; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch: enable console.error for recoverable errors in noop renderer
git apply - <<'PATCH'
diff --git a/packages/react-noop-renderer/src/createReactNoop.js b/packages/react-noop-renderer/src/createReactNoop.js
index 79d1e1a8c9bc..11f9f59c2c9a 100644
--- a/packages/react-noop-renderer/src/createReactNoop.js
+++ b/packages/react-noop-renderer/src/createReactNoop.js
@@ -1151,9 +1151,9 @@ function createReactNoop(reconciler: Function, useMutation: boolean) {
     }
   }

-  function onRecoverableError(error) {
-    // TODO: Turn this on once tests are fixed
-    // console.error(error);
+  function onRecoverableError(error: mixed): void {
+    // eslint-disable-next-line react-internal/warning-args, react-internal/no-production-logging -- renderer is only used for testing.
+    console.error(error);
   }
   function onDefaultTransitionIndicator(): void | (() => void) {}

PATCH

echo "Gold patch applied successfully"
