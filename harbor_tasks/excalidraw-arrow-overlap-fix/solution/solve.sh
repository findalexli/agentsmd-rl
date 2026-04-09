#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if patch already applied (idempotency)
if grep -q "const extractBinding =" packages/element/src/binding.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/packages/element/src/align.ts b/packages/element/src/align.ts
index 17ebc3a97c90..3068aee8d113 100644
--- a/packages/element/src/align.ts
+++ b/packages/element/src/align.ts
@@ -43,7 +43,6 @@ export const alignElements = (
       // update bound elements
       updateBoundElements(element, scene, {
         simultaneouslyUpdated: group,
-        indirectArrowUpdate: true,
       });
       return updatedEle;
     });
diff --git a/packages/element/src/arrows/focus.ts b/packages/element/src/arrows/focus.ts
index e0abd75f6698..fa8018adbe2e 100644
--- a/packages/element/src/arrows/focus.ts
+++ b/packages/element/src/arrows/focus.ts
@@ -141,6 +141,7 @@ const focusPointUpdate = (
       currentBinding,
       bindableElement,
       elementsMap,
+      true,
     );

     if (newPoint) {
diff --git a/packages/element/src/binding.ts b/packages/element/src/binding.ts
index e7bc98c04f2b..86041b4aba28 100644
--- a/packages/element/src/binding.ts
+++ b/packages/element/src/binding.ts
@@ -27,11 +27,7 @@ import type { AppState } from "@excalidraw/excalidraw/types";
 import type { MapEntry, Mutable } from "@excalidraw/common/utility-types";
 import type { Bounds } from "@excalidraw/common";

-import {
-  doBoundsIntersect,
-  getCenterForBounds,
-  getElementBounds,
-} from "./bounds";
+import { getCenterForBounds } from "./bounds";
 import {
   getAllHoveredElementAtPoint,
   getHoveredElementForBinding,
@@ -116,6 +112,7 @@ export type BindingStrategy =
  */
 export const BASE_BINDING_GAP = 5;
 export const BASE_BINDING_GAP_ELBOW = 5;
+export const BASE_ARROW_MIN_LENGTH = 10;
 export const FOCUS_POINT_SIZE = 10 / 1.5;

 export const getBindingGap = (
@@ -810,13 +807,23 @@ const getBindingStrategyForDraggingBindingElementEndpoints_simple = (
     startDragged ? -1 : 0,
     elementsMap,
   );
-
+  const pointIsCloseToOtherElement =
+    otherFocusPoint &&
+    otherBindableElement &&
+    hitElementItself({
+      point: globalPoint,
+      element: otherBindableElement,
+      elementsMap,
+      threshold: maxBindingDistance_simple(appState.zoom),
+      overrideShouldTestInside: true,
+    });
   const otherNeverOverride = opts?.newArrow
     ? appState.selectedLinearElement?.initialState.arrowStartIsInside
     : otherBinding?.mode === "inside";
   const other: BindingStrategy = !otherNeverOverride
     ? otherBindableElement &&
       !otherFocusPointIsInElement &&
+      !pointIsCloseToOtherElement &&
       appState.selectedLinearElement?.initialState.altFocusPoint
       ? {
           mode: "orbit",
@@ -1083,7 +1090,6 @@ export const updateBoundElements = (
   options?: {
     simultaneouslyUpdated?: readonly ExcalidrawElement[];
     changedElements?: Map<string, ExcalidrawElement>;
-    indirectArrowUpdate?: boolean;
   },
 ) => {
   if (!isBindableElement(changedElement)) {
@@ -1178,11 +1184,6 @@ export const updateBoundElements = (
   };

   boundElementsVisitor(elementsMap, changedElement, visitor);
-
-  if (options?.indirectArrowUpdate) {
-    boundElementsVisitor(elementsMap, changedElement, visitor);
-    boundElementsVisitor(elementsMap, changedElement, visitor);
-  }
 };

 const updateArrowBindings = (
@@ -1692,10 +1693,41 @@ export const snapToMid = (
   return undefined;
 };

-const compareElementArea = (
-  a: ExcalidrawBindableElement,
-  b: ExcalidrawBindableElement,
-) => b.width ** 2 + b.height ** 2 - (a.width ** 2 + a.height ** 2);
+const extractBinding = (
+  arrow: ExcalidrawArrowElement,
+  startOrEnd: "startBinding" | "endBinding",
+  elementsMap: ElementsMap,
+) => {
+  const binding = arrow[startOrEnd];
+  if (!binding) {
+    return {
+      element: null,
+      fixedPoint: null,
+      focusPoint: null,
+      binding,
+      mode: null,
+    };
+  }
+
+  const element = elementsMap.get(
+    binding.elementId,
+  ) as ExcalidrawBindableElement;
+
+  return {
+    element,
+    fixedPoint: binding.fixedPoint,
+    focusPoint: getGlobalFixedPointForBindableElement(
+      normalizeFixedPoint(binding.fixedPoint),
+      element,
+      elementsMap,
+    ),
+    binding,
+    mode: binding.mode,
+  };
+};
+
+const elementArea = (element: ExcalidrawBindableElement) =>
+  element.width * element.height;

 export const updateBoundPoint = (
   arrow: NonDeleted<ExcalidrawArrowElement>,
@@ -1703,9 +1735,7 @@ export const updateBoundPoint = (
   binding: FixedPointBinding | null | undefined,
   bindableElement: ExcalidrawBindableElement,
   elementsMap: ElementsMap,
-  opts?: {
-    customIntersector?: LineSegment<GlobalPoint>;
-  },
+  dragging?: boolean,
 ): LocalPoint | null => {
   if (
     binding == null ||
@@ -1720,150 +1750,136 @@ export const updateBoundPoint = (
     return null;
   }

-  const global = getGlobalFixedPointForBindableElement(
+  const focusPoint = getGlobalFixedPointForBindableElement(
     normalizeFixedPoint(binding.fixedPoint),
     bindableElement,
     elementsMap,
   );
-  const pointIndex =
-    startOrEnd === "startBinding" ? 0 : arrow.points.length - 1;
-  const elbowed = isElbowArrow(arrow);
-  const otherBinding =
-    startOrEnd === "startBinding" ? arrow.endBinding : arrow.startBinding;
-  const otherBindableElement =
-    otherBinding &&
-    (elementsMap.get(otherBinding.elementId)! as ExcalidrawBindableElement);
-  const bounds = getElementBounds(bindableElement, elementsMap);
-  const otherBounds =
-    otherBindableElement && getElementBounds(otherBindableElement, elementsMap);
-  const isLargerThanOther =
-    otherBindableElement &&
-    compareElementArea(bindableElement, otherBindableElement) <
-      // if both shapes the same size, pretend the other is larger
-      (startOrEnd === "endBinding" ? 1 : 0);
-  const isOverlapping = otherBounds && doBoundsIntersect(bounds, otherBounds);
-
-  // GOAL: If the arrow becomes too short, we want to jump the arrow endpoints
-  // to the exact focus points on the elements.
-  // INTUITION: We're not interested in the exacts length of the arrow (which
-  // will change if we change where we route it), we want to know the length of
-  // the part which lies outside of both shapes and consider that as a trigger
-  // to change where we point the arrow. Avoids jumping the arrow in and out
-  // at every frame.
-  let arrowTooShort = false;
-  if (
-    !isOverlapping &&
-    !elbowed &&
-    arrow.startBinding &&
-    arrow.endBinding &&
-    otherBindableElement &&
-    arrow.points.length === 2
-  ) {
-    const startFocusPoint = getGlobalFixedPointForBindableElement(
-      arrow.startBinding.fixedPoint,
-      startOrEnd === "startBinding" ? bindableElement : otherBindableElement,
+  // 0. Short-circuit for inside binding as it doesn't require any
+  // calculations and is not affected by other bindings
+  if (binding.mode === "inside") {
+    return LinearElementEditor.createPointAt(
+      arrow,
       elementsMap,
+      focusPoint[0],
+      focusPoint[1],
+      null,
     );
-    const endFocusPoint = getGlobalFixedPointForBindableElement(
-      arrow.endBinding.fixedPoint,
-      startOrEnd === "endBinding" ? bindableElement : otherBindableElement,
+  }
+
+  const { element: otherBindable, focusPoint: otherFocusPoint } =
+    extractBinding(
+      arrow,
+      startOrEnd === "startBinding" ? "endBinding" : "startBinding",
       elementsMap,
     );
-    const segment = lineSegment(startFocusPoint, endFocusPoint);
-    const startIntersection = intersectElementWithLineSegment(
-      startOrEnd === "endBinding" ? bindableElement : otherBindableElement,
+  const otherArrowPoint = LinearElementEditor.getPointAtIndexGlobalCoordinates(
+    arrow,
+    startOrEnd === "startBinding" ? -1 : 0,
+    elementsMap,
+  );
+  const otherFocusPointOrArrowPoint = otherFocusPoint || otherArrowPoint;
+  const intersector =
+    otherFocusPointOrArrowPoint &&
+    lineSegment(focusPoint, otherFocusPointOrArrowPoint);
+  const otherOutlinePoint =
+    otherBindable &&
+    intersector &&
+    intersectElementWithLineSegment(
+      otherBindable,
       elementsMap,
-      segment,
-      0,
-      true,
-    );
-    const endIntersection = intersectElementWithLineSegment(
-      startOrEnd === "startBinding" ? bindableElement : otherBindableElement,
+      intersector,
+      getBindingGap(otherBindable, arrow),
+    ).sort(
+      (a, b) => pointDistanceSq(a, focusPoint) - pointDistanceSq(b, focusPoint),
+    )[0];
+  const outlinePoint =
+    intersector &&
+    intersectElementWithLineSegment(
+      bindableElement,
       elementsMap,
-      segment,
-      0,
-      true,
+      intersector,
+      getBindingGap(bindableElement, arrow),
+    ).sort(
+      (a, b) =>
+        pointDistanceSq(a, otherFocusPointOrArrowPoint) -
+        pointDistanceSq(b, otherFocusPointOrArrowPoint),
+    )[0];
+  const startHasArrowhead = arrow.startArrowhead !== null;
+  const endHasArrowhead = arrow.endArrowhead !== null;
+  const resolvedTarget =
+    (!startHasArrowhead && !endHasArrowhead) ||
+    (startOrEnd === "startBinding" && startHasArrowhead) ||
+    (startOrEnd === "endBinding" && endHasArrowhead)
+      ? focusPoint
+      : outlinePoint || focusPoint;
+
+  // 1. Handle case when the outline point (or focus point) is inside
+  // the other shape by short-circuiting to the focus point, otherwise
+  // the arrow would invert
+  if (
+    otherBindable &&
+    outlinePoint &&
+    !dragging &&
+    // Arbitrary threshold to handle wireframing use cases
+    elementArea(otherBindable) < elementArea(bindableElement) * 2 &&
+    hitElementItself({
+      element: otherBindable,
+      point: outlinePoint,
+      elementsMap,
+      threshold: getBindingGap(otherBindable, arrow),
+      overrideShouldTestInside: true,
+    })
+  ) {
+    return LinearElementEditor.createPointAt(
+      arrow,
+      elementsMap,
+      resolvedTarget[0],
+      resolvedTarget[1],
+      null,
     );
-    if (startIntersection.length > 0 && endIntersection.length > 0) {
-      const len = pointDistance(startIntersection[0], endIntersection[0]);
-      arrowTooShort = len < 40;
-    }
   }

-  const isNested = (arrowTooShort || isOverlapping) && isLargerThanOther;
-
-  let _customIntersector = opts?.customIntersector;
-  if (!elbowed && !_customIntersector) {
-    const [x1, y1, x2, y2] = LinearElementEditor.getElementAbsoluteCoords(
+  const otherTargetPoint = otherBindable
+    ? otherOutlinePoint || otherFocusPoint || otherArrowPoint
+    : otherArrowPoint;
+  const arrowTooShort =
+    pointDistance(otherTargetPoint, outlinePoint || focusPoint) <=
+    BASE_ARROW_MIN_LENGTH;
+
+  // 2. If the arrow is unconnected at the other end, just check arrow size
+  // and short-circuit to the focus point if the arrow is too short to
+  // avoid inversion
+  if (!otherBindable) {
+    return LinearElementEditor.createPointAt(
       arrow,
       elementsMap,
-    );
-    const center = pointFrom<GlobalPoint>((x1 + x2) / 2, (y1 + y2) / 2);
-    const edgePoint = global;
-    const adjacentPoint = pointRotateRads(
-      pointFrom<GlobalPoint>(
-        arrow.x +
-          arrow.points[pointIndex === 0 ? 1 : arrow.points.length - 2][0],
-        arrow.y +
-          arrow.points[pointIndex === 0 ? 1 : arrow.points.length - 2][1],
-      ),
-      center,
-      arrow.angle as Radians,
-    );
-    const bindingGap = getBindingGap(bindableElement, arrow);
-    const halfVector = vectorScale(
-      vectorNormalize(vectorFromPoint(edgePoint, adjacentPoint)),
-      pointDistance(edgePoint, adjacentPoint) +
-        Math.max(bindableElement.width, bindableElement.height) +
-        bindingGap * 2,
-    );
-    _customIntersector = lineSegment(
-      pointFromVector(halfVector, adjacentPoint),
-      pointFromVector(vectorScale(halfVector, -1), adjacentPoint),
+      arrowTooShort ? focusPoint[0] : outlinePoint?.[0] ?? focusPoint[0],
+      arrowTooShort ? focusPoint[1] : outlinePoint?.[1] ?? focusPoint[1],
+      null,
     );
   }

-  const maybeOutlineGlobal =
-    binding.mode === "orbit" && bindableElement
-      ? isNested
-        ? global
-        : bindPointToSnapToElementOutline(
-            {
-              ...arrow,
-              points: [
-                pointIndex === 0
-                  ? LinearElementEditor.createPointAt(
-                      arrow,
-                      elementsMap,
-                      global[0],
-                      global[1],
-                      null,
-                    )
-                  : arrow.points[0],
-                ...arrow.points.slice(1, -1),
-                pointIndex === arrow.points.length - 1
-                  ? LinearElementEditor.createPointAt(
-                      arrow,
-                      elementsMap,
-                      global[0],
-                      global[1],
-                      null,
-                    )
-                  : arrow.points[arrow.points.length - 1],
-              ],
-            },
-            bindableElement,
-            pointIndex === 0 ? "start" : "end",
-            elementsMap,
-            _customIntersector,
-          )
-      : global;
+  // 3. If the arrow is too short while connected on both ends and
+  // the other arrow endpoint will not be inside the bindable, just
+  // check the arrow size and make a decision based on that
+  if (arrowTooShort) {
+    return LinearElementEditor.createPointAt(
+      arrow,
+      elementsMap,
+      resolvedTarget?.[0] || focusPoint[0],
+      resolvedTarget?.[1] || focusPoint[1],
+      null,
+    );
+  }

+  // 4. In the general case, snap to the outline if possible
   return LinearElementEditor.createPointAt(
     arrow,
     elementsMap,
-    maybeOutlineGlobal[0],
-    maybeOutlineGlobal[1],
+    outlinePoint?.[0] || focusPoint[0],
+    outlinePoint?.[1] || focusPoint[1],
     null,
   );
 };
diff --git a/packages/element/src/linearElementEditor.ts b/packages/element/src/linearElementEditor.ts
index 1664a578e2bf..e3d3f2e5105e 100644
--- a/packages/element/src/linearElementEditor.ts
+++ b/packages/element/src/linearElementEditor.ts
@@ -9,7 +9,6 @@ import {
   vectorFromPoint,
   curveLength,
   curvePointAtLength,
-  lineSegment,
 } from "@excalidraw/math";

 import { getCurvePathOps } from "@excalidraw/utils/shape";
@@ -2339,19 +2338,6 @@ const pointDraggingUpdates = (
         : updates.endBinding,
   };

-  // We need to use a custom intersector to ensure that if there is a big "jump"
-  // in the arrow's position, we can position it with outline avoidance
-  // pixel-perfectly and avoid "dancing" arrows.
-  // NOTE: Direction matters here, so we create two intersectors
-  const startCustomIntersector =
-    start.focusPoint && end.focusPoint
-      ? lineSegment(start.focusPoint, end.focusPoint)
-      : undefined;
-  const endCustomIntersector =
-    start.focusPoint && end.focusPoint
-      ? lineSegment(end.focusPoint, start.focusPoint)
-      : undefined;
-
   // Needed to handle a special case where an existing arrow is dragged over
   // the same element it is bound to on the other side
   const startIsDraggingOverEndElement =
@@ -2387,9 +2373,7 @@ const pointDraggingUpdates = (
         nextArrow.endBinding,
         endBindable,
         elementsMap,
-        {
-          customIntersector: endCustomIntersector,
-        },
+        endIsDragged,
       ) || nextArrow.points[nextArrow.points.length - 1]
     : nextArrow.points[nextArrow.points.length - 1];

@@ -2420,7 +2404,7 @@ const pointDraggingUpdates = (
           nextArrow.startBinding,
           startBindable,
           elementsMap,
-          { customIntersector: startCustomIntersector },
+          startIsDragged,
         ) || nextArrow.points[0]
       : nextArrow.points[0];

diff --git a/packages/element/src/utils.ts b/packages/element/src/utils.ts
index ee341b310ae6..7013acf2f136 100644
--- a/packages/element/src/utils.ts
+++ b/packages/element/src/utils.ts
@@ -43,6 +43,11 @@ import { LinearElementEditor } from "./linearElementEditor";
 import { isRectangularElement } from "./typeChecks";
 import { maxBindingDistance_simple } from "./binding";

+import {
+  getGlobalFixedPointForBindableElement,
+  normalizeFixedPoint,
+} from "./binding";
+
 import type {
   ElementsMap,
   ExcalidrawArrowElement,
@@ -677,11 +682,35 @@ export const projectFixedPointOntoDiagonal = (
     elementsMap,
   );

-  const a = LinearElementEditor.getPointAtIndexGlobalCoordinates(
+  // To avoid working with stale arrow state, we use the opposite focus point
+  // of the current endpoint, which will always be unchanged during moving of
+  // the endpoint. This is only needed when the arrow has only two points.
+  let a = LinearElementEditor.getPointAtIndexGlobalCoordinates(
     arrow,
     startOrEnd === "start" ? 1 : arrow.points.length - 2,
     elementsMap,
   );
+  if (arrow.points.length === 2) {
+    const otherBinding =
+      startOrEnd === "start" ? arrow.endBinding : arrow.startBinding;
+    const otherBindable =
+      otherBinding &&
+      (elementsMap.get(otherBinding.elementId) as
+        | ExcalidrawBindableElement
+        | undefined);
+    const otherFocusPoint =
+      otherBinding &&
+      otherBindable &&
+      getGlobalFixedPointForBindableElement(
+        normalizeFixedPoint(otherBinding.fixedPoint),
+        otherBindable,
+        elementsMap,
+      );
+    if (otherFocusPoint) {
+      a = otherFocusPoint;
+    }
+  }
+
   const b = pointFromVector<GlobalPoint>(
     vectorScale(
       vectorFromPoint(point, a),
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index fc8a40005555..32bac77e1e80 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -9623,9 +9623,7 @@ class App extends React.Component<AppProps, AppState> {
                   isBindableElement(element) &&
                   element.boundElements?.some((other) => other.type === "arrow")
                 ) {
-                  updateBoundElements(element, this.scene, {
-                    indirectArrowUpdate: true,
-                  });
+                  updateBoundElements(element, this.scene);
                 }
               });

diff --git a/packages/excalidraw/tests/__snapshots__/history.test.tsx.snap b/packages/excalidraw/tests/__snapshots__/history.test.tsx.snap
index 1dd0f92ceac2..c8c427e6aef7 100644
--- a/packages/excalidraw/tests/__snapshots__/history.test.tsx.snap
+++ b/packages/excalidraw/tests/__snapshots__/history.test.tsx.snap
@@ -227,7 +227,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 33,
+  "version": 29,
   "width": "94.00000",
   "x": 0,
   "y": 0,
@@ -334,15 +334,15 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "height": "105.58873",
+            "height": "105.58874",
             "points": [
               [
                 0,
                 0,
               ],
               [
-                88,
-                "105.58873",
+                "88.00000",
+                "105.58874",
               ],
             ],
             "startBinding": {
@@ -353,8 +353,8 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "version": 32,
-            "width": 88,
+            "version": 28,
+            "width": "88.00000",
           },
           "inserted": {
             "endBinding": {
@@ -365,7 +365,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "height": "0.00000",
+            "height": 0,
             "points": [
               [
                 0,
                 0,
               ],
               [
-                "0.00000",
+                0,
               ],
             ],
             "startBinding": {
@@ -384,7 +384,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "version": 29,
+            "version": 25,
             "width": "88.00000",
           },
         },
@@ -440,21 +440,21 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
             ],
             "startBinding": null,
-            "version": 33,
+            "version": 29,
             "width": "94.00000",
             "x": 0,
             "y": 0,
           },
           "inserted": {
-            "height": "105.58873",
+            "height": "105.58874",
             "points": [
               [
                 0,
                 0,
               ],
               [
-                88,
-                "105.58873",
               ],
+                "88.00000",
+                "105.58874",
               ],
             ],
             "startBinding": {
@@ -465,10 +465,10 @@ exports[`history `:
             "mode": "orbit",
             },
-            "version": 32,
-            "width": 88,
+            "version": 28,
+            "width": "88.00000",
             "x": 6,
-            "y": "7.09000",
+            "y": "7.20923",
           },
         },
       },
@@ -854,7 +854,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 30,
+  "version": 25,
   "width": 100,
   "x": 150,
   "y": 0,
@@ -904,15 +904,15 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
         "id4": {
           "deleted": {
             "endBinding": null,
-            "height": "0.00293",
+            "height": "0.01000",
             "points": [
               [
                 0,
                 0,
               ],
               [
-                "-44.00000",
-                "-0.00293",
+                -44,
+                "-0.01000",
               ],
             ],
             "startBinding": {
@@ -923,9 +923,9 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "version": 29,
-            "width": "44.00000",
-            "y": "0.00293",
+            "version": 24,
+            "width": 44,
+            "y": "0.01000",
           },
           "inserted": {
             "endBinding": {
@@ -943,7 +943,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
                 0,
               ],
               [
-                "6.00000",
+                -100,
                 0,
               ],
             ],
@@ -955,8 +955,8 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "version": 27,
-            "width": "6.00000",
+            "version": 23,
+            "width": 100,
             "y": "0.01000",
           },
         },
@@ -1004,21 +1004,21 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
             ],
             "startBinding": null,
-            "version": 30,
+            "version": 25,
             "width": 100,
             "x": 150,
             "y": 0,
           },
           "inserted": {
-            "height": "0.00293",
+            "height": "0.01000",
             "points": [
               [
                 0,
                 0,
               ],
               [
-                "-44.00000",
-                "-0.00293",
+                -44,
+                "-0.01000",
               ],
             ],
             "startBinding": {
@@ -1029,10 +1029,10 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
               ],
               "mode": "orbit",
             },
-            "version": 29,
-            "width": "44.00000",
-            "x": 144,
-            "y": "0.00293",
+            "version": 24,
+            "width": 44,
+            "x": 250,
+            "y": "0.01000",
           },
         },
       },
@@ -1335,7 +1335,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "29.36414",
+  "height": "29.32551",
   "id": "id4",
   "index": "Zz",
   "isDeleted": false,
@@ -1350,7 +1350,7 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
     ],
     [
       88,
-      "29.36414",
+      "29.32551",
     ],
   ],
   "roughness": 1,
@@ -1369,10 +1369,10 @@ exports[`history > multiplayer undo/redo > conflicts in arrows and their bindabl
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 10,
+  "version": 8,
   "width": 88,
   "x": 6,
-  "y": "2.00946",
+  "y": "2.00947",
 }

 exports[`history > multiplayer undo/redo > should support bidirectional binding
@@ -1546,7 +1546,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               ],
               "mode": "orbit",
             },
-            "version": 10,
+            "version": 8,
           },
           "inserted": {
             "endBinding": null,
@@ -1698,7 +1698,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "14.91372",
+  "height": "17.59718",
   "id": "id5",
   "index": "a0",
   "isDeleted": false,
@@ -1712,8 +1712,8 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
       0,
     ],
     [
-      "88.00000",
-      "-14.91372",
+      88,
+      "-17.59718",
     ],
   ],
   "roughness": 1,
@@ -1732,10 +1732,10 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 11,
-  "width": "88.00000",
+  "version": 8,
+  "width": 88,
   "x": 6,
-  "y": "37.05219",
+  "y": "38.80379",
 }

 exports[`history > multiplayer undo/redo > should support bidirectional binding
@@ -1846,7 +1846,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "14.91372",
+            "height": "17.59718",
             "index": "a0",
             "isDeleted": false,
             "link": "null",
@@ -1858,8 +1858,8 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               "mode": "orbit",
               "fixedPoint": [
                 0,
-                "0.00936",
+                "0.00120",
               ],
               [
-                88,
-                "0.00936",
+                "88.00000",
+                "0.00120",
               ],
             ],
             "roughness": 1,
@@ -1877,14 +1877,14 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 11,
-              "width": "88.00000",
+              "version": 8,
+              "width": 88,
               "x": 6,
-              "y": "37.05219",
+              "y": "38.80379",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 8,
+              "version": 7,
             },
           },
         },
@@ -2398,7 +2398,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "439.13521",
+            "height": "439.20000",
             "index": "a2",
             "isDeleted": false,
             "link": null,
@@ -2413,7 +2413,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               ],
               [
                 488,
-                "-439.13521",
+                "-439.20000",
               ],
             ],
             "roughness": 1,
@@ -2434,10 +2434,10 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 13,
+              "version": 12,
               "width": 488,
               "x": 6,
-              "y": "-5.38920",
+              "y": "-5.39000",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 10,
+              "version": 9,
             },
           },
         },
@@ -2566,7 +2566,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "439.13521",
+            "height": "439.20000",
             "index": "a2",
             "isDeleted": false,
             "link": null,
@@ -2579,7 +2579,7 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               ],
               [
                 488,
-                "-439.13521",
+                "-439.20000",
               ],
             ],
             "roughness": 1,
@@ -2599,14 +2599,14 @@ exports[`history > multiplayer undo/redo > should support bidirectional binding
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 13,
+              "version": 12,
               "width": 488,
               "x": 6,
-              "y": "-5.38920",
+              "y": "-5.39000",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 10,
+              "version": 9,
             },
           },
         },
@@ -16383,7 +16383,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional bindin
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "0.00004",
+  "height": 0,
   "id": "id13",
   "index": "a3",
   "isDeleted": false,
@@ -16398,7 +16398,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional bindin
     ],
     [
       "88.00000",
-      "0.00004",
+      0,
     ],
   ],
   "roughness": 1,
@@ -16419,10 +16419,10 @@ exports[`history > singleplayer undo/redo > should support bidirectional bindin
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 12,
+  "version": 10,
   "width": "88.00000",
   "x": 6,
-  "y": "0.00996",
+  "y": "0.01000",
 }
 `;

@@ -16472,7 +16472,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               "mode": "orbit",
             },
-            "version": 12,
+            "version": 10,
           },
           "inserted": {
             "endBinding": {
@@ -16492,7 +16492,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               "mode": "orbit",
             },
-            "version": 9,
+            "version": 8,
           },
         },
         "id2": {
@@ -16801,7 +16801,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "0.00936",
+            "height": "0.00120",
             "index": "a3",
             "isDeleted": false,
             "link": null,
@@ -16813,8 +16813,8 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
                 0,
               ],
               [
-                88,
-                "0.00936",
+                "88.00000",
+                "0.00120",
               ],
             ],
             "roughness": 1,
@@ -16834,14 +16834,14 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 8,
-              "width": 88,
+              "version": 7,
+              "width": "88.00000",
               "x": 6,
-              "y": 0,
+              "y": "0.00880",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 7,
+              "version": 6,
             },
           },
         },
@@ -17134,7 +17134,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "0.00004",
+  "height": 0,
   "id": "id13",
   "index": "a3",
   "isDeleted": false,
@@ -17149,7 +17149,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
     ],
     [
       "88.00000",
-      "0.00004",
+      0,
     ],
   ],
   "roughness": 1,
@@ -17170,10 +17170,10 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 12,
+  "version": 10,
   "width": "88.00000",
   "x": 6,
-  "y": "0.00996",
+  "y": "0.01000",
 }

 exports[`history > singleplayer undo/redo > should support bidirectional binding
@@ -17442,7 +17442,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "0.00004",
+            "height": 0,
             "index": "a3",
             "isDeleted": false,
             "link": null,
@@ -17455,7 +17455,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               [
                 "88.00000",
-                "0.00004",
+                0,
               ],
             ],
             "roughness": 1,
@@ -17475,14 +17475,14 @@ exports[`history > singleplayer detects">
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 12,
+              "version": 10,
               "width": "88.00000",
               "x": 6,
-              "y": "0.00996",
+              "y": "0.01000",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 9,
+              "version": 8,
             },
           },
         },
@@ -17783,7 +17783,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "0.00004",
+  "height": 0,
   "id": "id13",
   "index": "a3",
   "isDeleted": false,
@@ -17798,7 +17798,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
     ],
     [
       "88.00000",
-      "0.00004",
+      0,
     ],
   ],
   "roughness": 1,
@@ -17819,10 +17819,10 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 12,
+  "version": 10,
   "width": "88.00000",
   "x": 6,
-  "y": "0.00996",
+  "y": "0.01000",
 }

 exports[`history > singleplayer undo/redo > should support bidirectional binding
@@ -18091,7 +18091,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "0.00004",
+            "height": 0,
             "index": "a3",
             "isDeleted": false,
             "link": null,
@@ -18104,7 +18104,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               [
                 "88.00000",
-                "0.00004",
+                0,
               ],
             ],
             "roughness": 1,
@@ -18124,14 +18124,14 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
             "strokeStyle": "solid",
             "strokeWidth": 2,
             "type": "arrow",
-            "version": 12,
+            "version": 10,
             "width": "88.00000",
             "x": 6,
-            "y": "0.00996",
+            "y": "0.01000",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 9,
+              "version": 8,
             },
           },
         },
@@ -18430,7 +18430,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "0.00004",
+  "height": 0,
   "id": "id13",
   "index": "a3",
   "isDeleted": false,
@@ -18445,7 +18445,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
     ],
     [
       "88.00000",
-      "0.00004",
+      0,
     ],
   ],
   "roughness": 1,
@@ -18466,10 +18466,10 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "stroke": {
     "type": "arrow",
   "updated": 1,
-  "version": 13,
+  "version": 11,
   "width": "88.00000",
   "x": 6,
-  "y": "0.00996",
+  "y": "0.01000",
 }

 exports[`history > singleplayer undo/redo > should support bidirectional binding
@@ -18535,7 +18535,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               "mode": "orbit",
             },
-            "version": 13,
+            "version": 11,
           },
           "inserted": {
             "endBinding": {
@@ -18547,7 +18547,7 @@ exports[`history `:
               "mode": "orbit",
             },
             "startBinding": {
-            "version": 10,
+            "version": 9,
             },
           },
         },
@@ -18824,7 +18824,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "0.00936",
+            "height": "0.00120",
             "index": "a3",
             "isDeleted": false,
             "link": null,
@@ -18836,8 +18836,8 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
                 0,
               ],
               [
-                88,
-                "0.00936",
+                "88.00000",
+                "0.00120",
               ],
             ],
             "roughness": 1,
@@ -18857,14 +18857,14 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 8,
-              "width": 88,
+              "version": 7,
+              "width": "88.00000",
               "x": 6,
-              "y": 0,
+              "y": "0.00880",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 7,
+              "version": 6,
             },
           },
         },
@@ -19185,7 +19185,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "0.00004",
+  "height": 0,
   "id": "id13",
   "index": "a3",
   "isDeleted": false,
@@ -19200,7 +19200,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
     ],
     [
       "88.00000",
-      "0.00004",
+      0,
     ],
   ],
   "roughness": 1,
@@ -19221,10 +19221,10 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
   "strokeWidth": 2,
   "type": "arrow",
   "updated": 1,
-  "version": 13,
+  "version": 11,
   "width": "88.00000",
   "x": 6,
-  "y": "0.00996",
+  "y": "0.01000",
 }

 exports[`history > singleplayer undo/redo > should support bidirectional binding
@@ -19301,12 +19301,12 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               "mode": "orbit",
             },
-            "version": 13,
+            "version": 11,
           },
           "inserted": {
             "endBinding": null,
             "startBinding": null,
-            "version": 10,
+            "version": 9,
           },
         },
         "id2": {
@@ -19575,7 +19575,7 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
             "fillStyle": "solid",
             "frameId": null,
             "groupIds": [],
-            "height": "0.00936",
+            "height": "0.00120",
             "index": "a3",
             "isDeleted": false,
             "link": null,
@@ -19587,8 +19587,8 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               ],
               [
-                88,
-                "0.00936",
+                "88.00000",
+                "0.00120",
               ],
             ],
             "roughness": 1,
@@ -19608,14 +19608,14 @@ exports[`history > singleplayer undo/redo > should support bidirectional binding
               "strokeStyle": "solid",
               "strokeWidth": 2,
               "type": "arrow",
-              "version": 8,
-              "width": 88,
+              "version": 7,
+              "width": "88.00000",
               "x": 6,
-            "y": 0,
+              "y": "0.00880",
             },
             "inserted": {
               "isDeleted": true,
-              "version": 7,
+              "version": 6,
             },
           },
         },
@@ -19623,7 +19623,7 @@ diff --git a/packages/excalidraw/tests/__snapshots__/move.test.tsx.snap b/package

 exports[`move element > rectangles with binding arrow 7`] = `
 {
   "endBinding": {
     "elementId": "id3",
     "fixedPoint": [
       "-0.02000",
-      "0.47904",
+      "0.48010",
     ],
     "mode": "orbit",
   },
   "fillStyle": "solid",
   "frameId": null,
   "groupIds": [],
-  "height": "90.02554",
+  "height": "90.01760",
   "id": "id6",
   "index": "a2",
   "isDeleted": false,
@@ -204,7 +204,7 @@ exports[`move element > rectangles with binding arrow 7`] = `
     ],
     [
       89,
-      "90.02554",
+      "90.01760",
     ],
   ],
   "roughness": 1,
@@ -217,7 +217,7 @@ exports[`move element > rectangles with binding arrow 7`] = `
     "elementId": "id0",
     "fixedPoint": [
       "1.06000",
-      "0.55687",
+      "0.56011",
     ],
     "mode": "orbit",
   },
@@ -230,6 +230,6 @@ exports[`move element > rectangles with binding arrow 7`] = `
   "versionNonce": 271613161,
   "width": 89,
   "x": 106,
-  "y": "55.68677",
+  "y": "56.01120",
 }
 `;
PATCH

echo "Patch applied successfully"
