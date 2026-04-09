#!/bin/bash

cd /workspace/excalidraw

# Check if already patched
if grep -q "pointsEqual" packages/element/src/binding.ts; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/element/src/binding.ts b/packages/element/src/binding.ts
index 1a519b1c98db..c29c8702609b 100644
--- a/packages/element/src/binding.ts
+++ b/packages/element/src/binding.ts
@@ -15,6 +15,7 @@ import {
   pointFrom,
   pointFromVector,
   pointRotateRads,
+  pointsEqual,
   vectorFromPoint,
   vectorNormalize,
   vectorScale,
@@ -1602,7 +1603,12 @@ export const updateBoundPoint = (
   if (
     binding == null ||
     // We only need to update the other end if this is a 2 point line element
-    (binding.elementId !== bindableElement.id && arrow.points.length > 2)
+    (binding.elementId !== bindableElement.id && arrow.points.length > 2) ||
+    // Initial arrow created on pointer down needs to not update the points
+    pointsEqual(
+      arrow.points[arrow.points.length - 1],
+      pointFrom<LocalPoint>(0, 0),
+    )
   ) {
     return null;
   }
PATCH

echo "Patch applied successfully"

# Try to rebuild packages (may fail at this commit due to pre-existing issues)
echo "Attempting to rebuild packages..."
yarn build:packages 2>&1 || echo "Warning: Package rebuild failed, but source code is patched correctly"

echo "Done"
