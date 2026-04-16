#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if grep -q "updateBoundElements" packages/element/src/distribute.ts; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the fix patch
cat <<'PATCH' | git apply -
diff --git a/packages/element/src/distribute.ts b/packages/element/src/distribute.ts
index add3522acc3f..bb9c2708d2a8 100644
--- a/packages/element/src/distribute.ts
+++ b/packages/element/src/distribute.ts
@@ -1,10 +1,12 @@
 import type { AppState } from "@excalidraw/excalidraw/types";

+import { updateBoundElements } from "./binding";
 import { getCommonBoundingBox } from "./bounds";
-import { newElementWith } from "./mutateElement";

 import { getSelectedElementsByGroup } from "./groups";

+import type { Scene } from "./Scene";
+
 import type { ElementsMap, ExcalidrawElement } from "./types";

 export interface Distribution {
@@ -17,6 +19,7 @@ export const distributeElements = (
   elementsMap: ElementsMap,
   distribution: Distribution,
   appState: Readonly<AppState>,
+  scene: Scene,
 ): ExcalidrawElement[] => {
   const [start, mid, end, extent] =
     distribution.axis === "x"
@@ -66,12 +69,16 @@ export const distributeElements = (
         translation[distribution.axis] = pos - box[mid];
       }

-      return group.map((element) =>
-        newElementWith(element, {
+      return group.map((element) => {
+        const updatedElement = scene.mutateElement(element, {
           x: element.x + translation.x,
           y: element.y + translation.y,
-        }),
-      );
+        });
+        updateBoundElements(element, scene, {
+          simultaneouslyUpdated: group,
+        });
+        return updatedElement;
+      });
     });
   }

@@ -90,11 +97,15 @@ export const distributeElements = (
     pos += step;
     pos += box[extent];

-    return group.map((element) =>
-      newElementWith(element, {
+    return group.map((element) => {
+      const updatedElement = scene.mutateElement(element, {
         x: element.x + translation.x,
         y: element.y + translation.y,
-      }),
-    );
+      });
+      updateBoundElements(element, scene, {
+        simultaneouslyUpdated: group,
+      });
+      return updatedElement;
+    });
   });
 };
diff --git a/packages/excalidraw/actions/actionDistribute.tsx b/packages/excalidraw/actions/actionDistribute.tsx
index 88e085f1de49..6c756034786f 100644
--- a/packages/excalidraw/actions/actionDistribute.tsx
+++ b/packages/excalidraw/actions/actionDistribute.tsx
@@ -58,6 +58,7 @@ const distributeSelectedElements = (
     app.scene.getNonDeletedElementsMap(),
     distribution,
     appState,
+    app.scene,
   );

   const updatedElementsMap = arrayToMap(updatedElements);
diff --git a/packages/excalidraw/wysiwyg/textWysiwyg.tsx b/packages/excalidraw/wysiwyg/textWysiwyg.tsx
index 90a4e101e768..52c80e9c6577 100644
--- a/packages/excalidraw/wysiwyg/textWysiwyg.tsx
+++ b/packages/excalidraw/wysiwyg/textWysiwyg.tsx
@@ -14,6 +14,7 @@ import {

 import {
   originalContainerCache,
+  updateBoundElements,
   updateOriginalContainerCache,
 } from "@excalidraw/element";

@@ -208,6 +209,7 @@ export const textWysiwyg = ({
           );

           app.scene.mutateElement(container, { height: targetContainerHeight });
+          updateBoundElements(container, app.scene);
           return;
         } else if (
           // autoshrink container height until original container height
@@ -221,6 +223,7 @@ export const textWysiwyg = ({
             container.type,
           );
           app.scene.mutateElement(container, { height: targetContainerHeight });
+          updateBoundElements(container, app.scene);
         } else {
           const { x, y } = computeBoundTextPosition(
             container,
PATCH

echo "Patch applied successfully!"
