#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already patched
if grep -q "previousPointerMoveCoords" packages/excalidraw/components/App.tsx 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index e224ca97db6a..bbd748d8a895 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -648,7 +648,10 @@ class App extends React.Component<AppProps, AppState> {
   lastPointerUpEvent: React.PointerEvent<HTMLElement> | PointerEvent | null =
     null;
   lastPointerMoveEvent: PointerEvent | null = null;
+  /** current frame pointer cords */
   lastPointerMoveCoords: { x: number; y: number } | null = null;
+  /** previous frame pointer coords */
+  previousPointerMoveCoords: { x: number; y: number } | null = null;
   lastViewportPosition = { x: 0, y: 0 };

   animationFrameHandler = new AnimationFrameHandler();
@@ -9020,8 +9023,8 @@ class App extends React.Component<AppProps, AppState> {
       }

       const lastPointerCoords =
-        this.lastPointerMoveCoords ?? pointerDownState.origin;
-      this.lastPointerMoveCoords = pointerCoords;
+        this.previousPointerMoveCoords ?? pointerDownState.origin;
+      this.previousPointerMoveCoords = pointerCoords;

       // We need to initialize dragOffsetXY only after we've updated
       // `state.selectedElementIds` on pointerDown. Doing it here in pointerMove
@@ -9388,13 +9391,13 @@ class App extends React.Component<AppProps, AppState> {
                 const nextCrop = {
                   ...crop,
                   x: clamp(
-                    crop.x +
+                    crop.x -
                       offsetVector[0] * Math.sign(croppingElement.scale[0]),
                     0,
                     image.naturalWidth - crop.width,
                   ),
                   y: clamp(
-                    crop.y +
+                    crop.y -
                       offsetVector[1] * Math.sign(croppingElement.scale[1]),
                     0,
                     image.naturalHeight - crop.height,
@@ -9887,6 +9890,7 @@ class App extends React.Component<AppProps, AppState> {

       // just in case, tool changes mid drag, always clean up
       this.lassoTrail.endPath();
+      this.previousPointerMoveCoords = null;

       SnapCache.setReferenceSnapPoints(null);
       SnapCache.setVisibleGaps(null);
PATCH

echo "Patch applied successfully"
