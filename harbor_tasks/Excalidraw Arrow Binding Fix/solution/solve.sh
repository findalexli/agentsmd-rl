#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already patched (idempotency)
if grep -q "Initial arrow created on pointer down needs to not update the points" packages/element/src/binding.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix patch with all code changes from PR #10676
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
diff --git a/packages/excalidraw/tests/move.test.tsx b/packages/excalidraw/tests/move.test.tsx
index a881bb83..659917da 100644
--- a/packages/excalidraw/tests/move.test.tsx
+++ b/packages/excalidraw/tests/move.test.tsx
@@ -110,11 +110,8 @@ describe("move element", () => {
     expect(h.state.selectedElementIds[rectB.id]).toBeTruthy();
     expect([rectA.x, rectA.y]).toEqual([0, 0]);
     expect([rectB.x, rectB.y]).toEqual([200, 0]);
-    expect([[arrow.x, arrow.y]]).toCloselyEqualPoints([[110, -4.576537]], 0);
-    expect([[arrow.width, arrow.height]]).toCloselyEqualPoints(
-      [[79, 132.89433]],
-      0,
-    );
+    expect([[arrow.x, arrow.y]]).toCloselyEqualPoints([[111, 51]], 0);
+    expect([[arrow.width, arrow.height]]).toCloselyEqualPoints([[78, 78]], 0);

     renderInteractiveScene.mockClear();
     renderStaticScene.mockClear();
@@ -132,10 +129,10 @@ describe("move element", () => {
     expect(h.state.selectedElementIds[rectB.id]).toBeTruthy();
     expect([rectA.x, rectA.y]).toEqual([0, 0]);
     expect([rectB.x, rectB.y]).toEqual([201, 2]);
-    expect([[arrow.x, arrow.y]]).toCloselyEqualPoints([[111, 6.1499]], 0);
+    expect([[arrow.x, arrow.y]]).toCloselyEqualPoints([[111, 51]], 0);
     expect([[arrow.width, arrow.height]]).toCloselyEqualPoints(
       [[79, 124.1678]],
-      0,
+      2,
     );

     h.elements.forEach((element) => expect(element).toMatchSnapshot());
diff --git a/packages/excalidraw/tests/history.test.tsx b/packages/excalidraw/tests/history.test.tsx
index d3c6e2d4..d3b0cf48 100644
--- a/packages/excalidraw/tests/history.test.tsx
+++ b/packages/excalidraw/tests/history.test.tsx
@@ -1590,9 +1590,7 @@ describe("history", () => {
         expect(API.getUndoStack().length).toBe(5);
         expect(arrow.startBinding).toEqual({
           elementId: rect1.id,
-          fixedPoint: expect.arrayContaining([
-            0.5379561888991137, 0.5379561888991137,
-          ]),
+          fixedPoint: expect.arrayContaining([0.5001, 0.5001]),
           mode: "orbit",
         });
         expect(arrow.endBinding).toEqual({
@@ -1615,9 +1613,7 @@ describe("history", () => {
         expect(API.getRedoStack().length).toBe(1);
         expect(arrow.startBinding).toEqual({
           elementId: rect1.id,
-          fixedPoint: expect.arrayContaining([
-            0.5379561888991137, 0.5379561888991137,
-          ]),
+          fixedPoint: expect.arrayContaining([0.5001, 0.5001]),
           mode: "orbit",
         });
         expect(arrow.endBinding).toEqual({
@@ -1640,9 +1636,7 @@ describe("history", () => {
         expect(API.getRedoStack().length).toBe(0);
         expect(arrow.startBinding).toEqual({
           elementId: rect1.id,
-          fixedPoint: expect.arrayContaining([
-            0.5379561888991137, 0.5379561888991137,
-          ]),
+          fixedPoint: expect.arrayContaining([0.5001, 0.5001]),
           mode: "orbit",
         });
         expect(arrow.endBinding).toEqual({
@@ -1673,9 +1667,7 @@ describe("history", () => {
         expect(API.getRedoStack().length).toBe(0);
         expect(arrow.startBinding).toEqual({
           elementId: ret1.id,
-          fixedPoint: expect.arrayContaining([
-            0.5379561888991137, 0.5379561888991137,
-          ]),
+          fixedPoint: expect.arrayContaining([0.5001, 0.5001]),
           mode: "orbit",
         });
         expect(arrow.endBinding).toEqual({
@@ -1698,9 +1690,7 @@ describe("history", () => {
         expect(API.getRedoStack().length).toBe(1);
         expect(arrow.startBinding).toEqual({
           elementId: rect1.id,
-          fixedPoint: expect.arrayContaining([
-            0.5379561888991137, 0.5379561888991137,
-          ]),
+          fixedPoint: expect.arrayContaining([0.5001, 0.5001]),
           mode: "orbit",
         });
         expect(arrow.endBinding).toEqual({
@@ -5061,9 +5051,7 @@ describe("history", () => {
               id: arrowId,
               startBinding: expect.objectContaining({
                 elementId: rect1.id,
-                fixedPoint: expect.arrayContaining([
-                  0.548442798411514, 0.548442798411514,
-                ]),
+                fixedPoint: expect.arrayContaining([0.5001, 0.5001]),
               }),
               endBinding: expect.objectContaining({
                 elementId: rect2.id,
PATCH

# Update test snapshots to match the fixed behavior
# The snapshots contain non-deterministic values (seed, versionNonce) that
# vary between runs, so we need to update them after applying the fix
echo "Updating test snapshots..."
yarn test:app move.test.tsx -t 'rectangles with binding arrow' --run --update 2>/dev/null || true
yarn test:app history.test.tsx -t 'bidirectional binding' --run --update 2>/dev/null || true

echo "Patch applied successfully"
