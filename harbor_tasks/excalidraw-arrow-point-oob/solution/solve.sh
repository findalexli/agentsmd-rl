#!/usr/bin/env bash
# Apply the gold patch from PR https://github.com/excalidraw/excalidraw/pull/10922.
# Idempotent: a distinctive line from the patch is checked first.
set -euo pipefail

cd /workspace/excalidraw

# Idempotency guard: a distinctive line introduced by the gold patch.
if grep -q "Fall back to the actual last point as a last resort." \
        packages/element/src/linearElementEditor.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/element/src/linearElementEditor.ts b/packages/element/src/linearElementEditor.ts
index e57211abbcb7..2ef5d5377686 100644
--- a/packages/element/src/linearElementEditor.ts
+++ b/packages/element/src/linearElementEditor.ts
@@ -476,16 +476,22 @@ export class LinearElementEditor {
       });
     }

-    invariant(
-      lastClickedPoint > -1 &&
-        selectedPointsIndices.includes(lastClickedPoint) &&
-        element.points[lastClickedPoint],
-      `There must be a valid lastClickedPoint in order to drag it. selectedPointsIndices(${JSON.stringify(
-        selectedPointsIndices,
-      )}) points(0..${
-        element.points.length - 1
-      }) lastClickedPoint(${lastClickedPoint})`,
-    );
+    if (
+      lastClickedPoint < 0 ||
+      !selectedPointsIndices.includes(lastClickedPoint) ||
+      !element.points[lastClickedPoint]
+    ) {
+      console.error(
+        `There must be a valid lastClickedPoint in order to drag it. selectedPointsIndices(${JSON.stringify(
+          selectedPointsIndices,
+        )}) points(0..${
+          element.points.length - 1
+        }) lastClickedPoint(${lastClickedPoint})`,
+      );
+
+      // Fall back to the actual last point as a last resort.
+      lastClickedPoint = element.points.length - 1;
+    }

     // point that's being dragged (out of all selected points)
     const draggingPoint = element.points[lastClickedPoint];
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index 09f059d2abb0..39c892c97c9a 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -6725,27 +6725,23 @@ class App extends React.Component<AppProps, AppState> {
           },
           { informMutation: false, isDragging: false },
         );
+        const newLastIdx = multiElement.points.length - 1;
         this.setState({
           selectedLinearElement: {
             ...selectedLinearElement,
-            selectedPointsIndices:
-              selectedLinearElement.selectedPointsIndices?.includes(
-                multiElement.points.length,
-              )
-                ? [
-                    ...selectedLinearElement.selectedPointsIndices.filter(
-                      (idx) =>
-                        idx !== multiElement.points.length &&
-                        idx !== multiElement.points.length - 1,
+            selectedPointsIndices: selectedLinearElement.selectedPointsIndices
+              ? [
+                  ...new Set(
+                    selectedLinearElement.selectedPointsIndices.map((idx) =>
+                      Math.min(idx, newLastIdx),
                     ),
-                    multiElement.points.length - 1,
-                  ]
-                : selectedLinearElement.selectedPointsIndices,
-            lastCommittedPoint:
-              multiElement.points[multiElement.points.length - 1],
+                  ),
+                ]
+              : selectedLinearElement.selectedPointsIndices,
+            lastCommittedPoint: multiElement.points[newLastIdx],
             initialState: {
               ...selectedLinearElement.initialState,
-              lastClickedPoint: multiElement.points.length - 1,
+              lastClickedPoint: newLastIdx,
             },
           },
         });
diff --git a/packages/excalidraw/data/restore.ts b/packages/excalidraw/data/restore.ts
index b77f010bd8e7..a3b861947d66 100644
--- a/packages/excalidraw/data/restore.ts
+++ b/packages/excalidraw/data/restore.ts
@@ -250,7 +250,9 @@ const repairBinding = <T extends ExcalidrawArrowElement>(
       };
     }

-    console.error(`could not repair binding for element`);
+    console.error(
+      `Could not repair binding for element "${boundElement?.id}" out of (${elementsMap?.size}) elements`,
+    );
   } catch (error) {
     console.error("Error repairing binding:", error);
   }
PATCH

echo "Patch applied successfully."
