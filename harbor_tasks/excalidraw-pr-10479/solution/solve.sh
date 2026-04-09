#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if git diff HEAD | grep -q "angleLocked?: boolean;"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/element/src/binding.ts b/packages/element/src/binding.ts
index c3fcf2767b00..0b39ddad5813 100644
--- a/packages/element/src/binding.ts
+++ b/packages/element/src/binding.ts
@@ -151,6 +151,7 @@ export const bindOrUnbindBindingElement = (
   opts?: {
     newArrow?: boolean;
     altKey?: boolean;
+    angleLocked?: boolean;
     initialBinding?: boolean;
   },
 ) => {
@@ -561,7 +562,7 @@ export const getBindingStrategyForDraggingBindingElementEndpoints = (
   appState: AppState,
   opts?: {
     newArrow?: boolean;
-    shiftKey?: boolean;
+    angleLocked?: boolean;
     altKey?: boolean;
     finalize?: boolean;
     initialBinding?: boolean;
@@ -597,7 +598,7 @@ const getBindingStrategyForDraggingBindingElementEndpoints_simple = (
   appState: AppState,
   opts?: {
     newArrow?: boolean;
-    shiftKey?: boolean;
+    angleLocked?: boolean;
     altKey?: boolean;
     finalize?: boolean;
     initialBinding?: boolean;
@@ -770,6 +771,12 @@ const getBindingStrategyForDraggingBindingElementEndpoints_simple = (
         }
     : { mode: null };

+  const otherEndpoint = LinearElementEditor.getPointAtIndexGlobalCoordinates(
+    arrow,
+    startDragged ? -1 : 0,
+    elementsMap,
+  );
+
   const other: BindingStrategy =
     otherBindableElement &&
     !otherFocusPointIsInElement &&
@@ -779,6 +786,19 @@ const getBindingStrategyForDraggingBindingElementEndpoints_simple = (
           element: otherBindableElement,
           focusPoint: appState.selectedLinearElement.initialState.altFocusPoint,
         }
+      : opts?.angleLocked && otherBindableElement
+      ? {
+          mode: "orbit",
+          element: otherBindableElement,
+          focusPoint:
+            projectFixedPointOntoDiagonal(
+              arrow,
+              otherEndpoint,
+              otherBindableElement,
+              startDragged ? "end" : "start",
+              elementsMap,
+            ) || otherEndpoint,
+        }
       : { mode: undefined };

   return {
diff --git a/packages/element/src/linearElementEditor.ts b/packages/element/src/linearElementEditor.ts
index 7e7f662786f7..7dd834a621d3 100644
--- a/packages/element/src/linearElementEditor.ts
+++ b/packages/element/src/linearElementEditor.ts
@@ -26,7 +26,6 @@ import {

 import {
   deconstructLinearOrFreeDrawElement,
-  getHoveredElementForBinding,
   isPathALoop,
   moveArrowAboveBindable,
   projectFixedPointOntoDiagonal,
@@ -306,21 +305,11 @@ export class LinearElementEditor {
     const customLineAngle =
       linearElementEditor.customLineAngle ??
       determineCustomLinearAngle(pivotPoint, element.points[idx]);
-    const hoveredElement = getHoveredElementForBinding(
-      pointFrom<GlobalPoint>(scenePointerX, scenePointerY),
-      elements,
-      elementsMap,
-    );

     // Determine if point movement should happen and how much
     let deltaX = 0;
     let deltaY = 0;
-    if (
-      shouldRotateWithDiscreteAngle(event) &&
-      !hoveredElement &&
-      !element.startBinding &&
-      !element.endBinding
-    ) {
+    if (shouldRotateWithDiscreteAngle(event)) {
       const [width, height] = LinearElementEditor._getShiftLockedDelta(
         element,
         elementsMap,
@@ -358,7 +347,7 @@ export class LinearElementEditor {
       element,
       elements,
       app,
-      event.shiftKey,
+      shouldRotateWithDiscreteAngle(event),
       event.altKey,
     );

@@ -492,22 +481,11 @@ export class LinearElementEditor {
     const endIsSelected = selectedPointsIndices.includes(
       element.points.length - 1,
     );
-    const hoveredElement = getHoveredElementForBinding(
-      pointFrom<GlobalPoint>(scenePointerX, scenePointerY),
-      elements,
-      elementsMap,
-    );

     // Determine if point movement should happen and how much
     let deltaX = 0;
     let deltaY = 0;
-    if (
-      shouldRotateWithDiscreteAngle(event) &&
-      singlePointDragged &&
-      !hoveredElement &&
-      !element.startBinding &&
-      !element.endBinding
-    ) {
+    if (shouldRotateWithDiscreteAngle(event) && singlePointDragged) {
       const [width, height] = LinearElementEditor._getShiftLockedDelta(
         element,
         elementsMap,
@@ -545,7 +523,7 @@ export class LinearElementEditor {
       element,
       elements,
       app,
-      event.shiftKey,
+      shouldRotateWithDiscreteAngle(event) && singlePointDragged,
       event.altKey,
     );

@@ -2092,7 +2070,7 @@ const pointDraggingUpdates = (
   element: NonDeleted<ExcalidrawLinearElement>,
   elements: readonly Ordered<NonDeletedExcalidrawElement>[],
   app: AppClassProperties,
-  shiftKey: boolean,
+  angleLocked: boolean,
   altKey: boolean,
 ): {
   positions: PointsPositionUpdates;
@@ -2133,7 +2111,7 @@ const pointDraggingUpdates = (
     app.state,
     {
       newArrow: !!app.state.newElement,
-      shiftKey,
+      angleLocked,
       altKey,
     },
   );
diff --git a/packages/excalidraw/actions/actionFinalize.tsx b/packages/excalidraw/actions/actionFinalize.tsx
index 97d4f5655aa3..d6c9287f6cc1 100644
--- a/packages/excalidraw/actions/actionFinalize.tsx
+++ b/packages/excalidraw/actions/actionFinalize.tsx
@@ -18,6 +18,7 @@ import {
   KEYS,
   arrayToMap,
   invariant,
+  shouldRotateWithDiscreteAngle,
   updateActiveTool,
 } from "@excalidraw/common";
 import { isPathALoop } from "@excalidraw/element";
@@ -105,6 +106,7 @@ export const actionFinalize = register<FormData>({
         bindOrUnbindBindingElement(element, draggedPoints, scene, appState, {
           newArrow,
           altKey: event.altKey,
+          angleLocked: shouldRotateWithDiscreteAngle(event),
         });
       } else if (isLineElement(element)) {
         if (
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index 36abd632b625..f4190fe8fa26 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -8619,7 +8619,12 @@ class App extends React.Component<AppProps, AppState> {
           ]),
           this.scene,
           this.state,
-          { newArrow: true, altKey: event.altKey, initialBinding: true },
+          {
+            newArrow: true,
+            altKey: event.altKey,
+            initialBinding: true,
+            angleLocked: shouldRotateWithDiscreteAngle(event.nativeEvent),
+          },
         );
       }
PATCH

echo "Patch applied successfully"
