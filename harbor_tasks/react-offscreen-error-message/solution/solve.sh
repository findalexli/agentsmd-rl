#!/usr/bin/env bash
# Apply the gold patch for the Offscreen error message fix
set -euo pipefail

# Check if already applied (idempotency)
if grep -q "fiber.return !== null" packages/react-reconciler/src/getComponentNameFromFiber.js; then
    echo "Patch already applied."
    exit 0
fi

echo "Applying Offscreen error message fix..."

git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/getComponentNameFromFiber.js b/packages/react-reconciler/src/getComponentNameFromFiber.js
index 97124bbf5ba5..8719539cfc08 100644
--- a/packages/react-reconciler/src/getComponentNameFromFiber.js
+++ b/packages/react-reconciler/src/getComponentNameFromFiber.js
@@ -122,7 +122,10 @@ export default function getComponentNameFromFiber(fiber: Fiber): string | null {
       }
       return 'Mode';
     case OffscreenComponent:
-      return 'Offscreen';
+      if (fiber.return !== null) {
+        return getComponentNameFromFiber(fiber.return);
+      }
+      return null;
     case Profiler:
       return 'Profiler';
     case ScopeComponent:
PATCH

echo "Patch applied successfully."
