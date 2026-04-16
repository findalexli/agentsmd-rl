#!/bin/bash
set -e

cd /workspace/excalidraw

# Apply the gold patch for caching hit detection in collision.ts
patch -p1 <<'PATCH'
diff --git a/packages/element/src/collision.ts b/packages/element/src/collision.ts
index a96c3ebc142a..d93363a4d89b 100644
--- a/packages/element/src/collision.ts
+++ b/packages/element/src/collision.ts
@@ -105,6 +105,12 @@ export type HitTestArgs = {
   overrideShouldTestInside?: boolean;
 };

+let cachedPoint: GlobalPoint | null = null;
+let cachedElement: WeakRef<ExcalidrawElement> | null = null;
+let cachedThreshold: number = Infinity;
+let cachedHit: boolean = false;
+let cachedOverrideShouldTestInside = false;
+
 export const hitElementItself = ({
   point,
   element,
@@ -113,6 +119,24 @@ export const hitElementItself = ({
   frameNameBound = null,
   overrideShouldTestInside = false,
 }: HitTestArgs) => {
+  // Return cached result if the same point and element version is tested again
+  if (
+    cachedPoint &&
+    pointsEqual(point, cachedPoint) &&
+    cachedThreshold <= threshold &&
+    overrideShouldTestInside === cachedOverrideShouldTestInside
+  ) {
+    const derefElement = cachedElement?.deref();
+    if (
+      derefElement &&
+      derefElement.id === element.id &&
+      derefElement.version === element.version &&
+      derefElement.versionNonce === element.versionNonce
+    ) {
+      return cachedHit;
+    }
+  }
+
   // Hit test against a frame's name
   const hitFrameName = frameNameBound
     ? isPointWithinBounds(
@@ -153,7 +177,16 @@ export const hitElementItself = ({
       isPointOnElementOutline(point, element, elementsMap, threshold)
     : isPointOnElementOutline(point, element, elementsMap, threshold);

-  return hitElement || hitFrameName;
+  const result = hitElement || hitFrameName;
+
+  // Cache end result
+  cachedPoint = point;
+  cachedElement = new WeakRef(element);
+  cachedThreshold = threshold;
+  cachedOverrideShouldTestInside = overrideShouldTestInside;
+  cachedHit = result;
+
+  return result;
 };

 export const hitElementBoundingBox = (
PATCH

# Verify the patch was applied
grep -q "cachedPoint: GlobalPoint | null = null" packages/element/src/collision.ts && echo "Patch applied successfully" || (echo "Patch failed" && exit 1)
