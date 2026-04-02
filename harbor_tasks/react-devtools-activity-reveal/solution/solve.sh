#!/bin/bash
set -euo pipefail

# Solution: Fix crash when revealing stable, filtered <Activity> children
# This adds the missing mount path when Activity transitions from hidden to visible

# Check if already applied
if grep -q "Since we don't mount hidden children and unmount children when hiding" /workspace/react/packages/react-devtools-shared/src/backend/fiber/renderer.js 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index bc1b2a590d59..72d22d88f99c 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -5405,6 +5405,17 @@ export function attach(
           // We're hiding the children. Remove them from the Frontend
           unmountRemainingChildren();
         }
+      } else if (prevWasHidden && !nextIsHidden) {
+        // Since we don't mount hidden children and unmount children when hiding,
+        // we need to enter the mount path when revealing.
+        const nextChildSet = nextFiber.child;
+        if (nextChildSet !== null) {
+          mountChildrenRecursively(
+            nextChildSet,
+            traceNearestHostComponentUpdate,
+          );
+          updateFlags |= ShouldResetChildren | ShouldResetSuspenseChildren;
+        }
       } else if (
         nextFiber.tag === SuspenseComponent &&
         OffscreenComponent !== -1 &&
PATCH

echo "Patch applied successfully"
