#!/bin/bash
set -e

cd /workspace/excalidraw

# Idempotency check: if already patched, exit early
if grep -q "image.naturalWidth / uncroppedSize.width" packages/excalidraw/components/App.tsx; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index bbd748d8a895..fa9a02b492b2 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -11,7 +11,6 @@ import {
   pointDistance,
   vector,
   pointRotateRads,
-  vectorScale,
   vectorFromPoint,
   vectorSubtract,
   vectorDot,
@@ -255,6 +254,7 @@ import {
   handleFocusPointPointerDown,
   handleFocusPointPointerUp,
   maybeHandleArrowPointlikeDrag,
+  getUncroppedWidthAndHeight,
 } from "@excalidraw/element";

 import type { GlobalPoint, LocalPoint, Radians } from "@excalidraw/math";
@@ -9341,14 +9341,21 @@ class App extends React.Component<AppProps, AppState> {
                 this.imageCache.get(croppingElement.fileId)?.image;

               if (image && !(image instanceof Promise)) {
-                const instantDragOffset = vectorScale(
-                  vector(
-                    pointerCoords.x - lastPointerCoords.x,
-                    pointerCoords.y - lastPointerCoords.y,
-                  ),
-                  Math.max(this.state.zoom.value, 2),
+                const uncroppedSize =
+                  getUncroppedWidthAndHeight(croppingElement);
+                const instantDragOffset = vector(
+                  pointerCoords.x - lastPointerCoords.x,
+                  pointerCoords.y - lastPointerCoords.y,
                 );

+                // to reduce cursor:image drift, we need to take into account
+                // the canvas image element scaling so we can accurately
+                // track the pixels on movement
+                instantDragOffset[0] *=
+                  image.naturalWidth / uncroppedSize.width;
+                instantDragOffset[1] *=
+                  image.naturalHeight / uncroppedSize.height;
+
                 const [x1, y1, x2, y2, cx, cy] = getElementAbsoluteCoords(
                   croppingElement,
                   elementsMap,
PATCH

echo "Patch applied successfully."
