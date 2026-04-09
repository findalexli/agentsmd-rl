#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already patched (idempotency check)
if grep -q "Error repairing binding:" packages/excalidraw/data/restore.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/excalidraw/data/restore.ts b/packages/excalidraw/data/restore.ts
index 31e3563dffa6..b78fa07f8407 100644
--- a/packages/excalidraw/data/restore.ts
+++ b/packages/excalidraw/data/restore.ts
@@ -136,99 +136,103 @@ const repairBinding = <T extends ExcalidrawArrowElement>(
   existingElementsMap: Readonly<ElementsMap> | null | undefined,
   startOrEnd: "start" | "end",
 ): FixedPointBinding | null => {
-  if (!binding) {
-    return null;
-  }
-
-  // ---------------------------------------------------------------------------
-  // elbow arrows
-  // ---------------------------------------------------------------------------
+  try {
+    if (!binding) {
+      return null;
+    }

-  if (isElbowArrow(element)) {
-    const fixedPointBinding:
-      | ExcalidrawElbowArrowElement["startBinding"]
-      | ExcalidrawElbowArrowElement["endBinding"] = {
-      ...binding,
-      fixedPoint: normalizeFixedPoint(binding.fixedPoint ?? [0, 0]),
-      mode: binding.mode || "orbit",
-    };
+    // ---------------------------------------------------------------------------
+    // elbow arrows
+    // ---------------------------------------------------------------------------
+
+    if (isElbowArrow(element)) {
+      const fixedPointBinding:
+        | ExcalidrawElbowArrowElement["startBinding"]
+        | ExcalidrawElbowArrowElement["endBinding"] = {
+        ...binding,
+        fixedPoint: normalizeFixedPoint(binding.fixedPoint ?? [0, 0]),
+        mode: binding.mode || "orbit",
+      };

-    return fixedPointBinding;
-  }
+      return fixedPointBinding;
+    }

-  // ---------------------------------------------------------------------------
-  // simple arrows
-  // ---------------------------------------------------------------------------
+    // ---------------------------------------------------------------------------
+    // simple arrows
+    // ---------------------------------------------------------------------------
+
+    // binding schema v2
+    // ---------------------------------------------------------------------------
+
+    if (binding.mode) {
+      // if latest binding schema, don't check if binding.elementId exists
+      // (it's done in a separate pass)
+      if (binding.elementId) {
+        return {
+          elementId: binding.elementId,
+          mode: binding.mode,
+          fixedPoint: normalizeFixedPoint(binding.fixedPoint || [0.5, 0.5]),
+        } as FixedPointBinding | null;
+      }
+      return null;
+    }

-  // binding schema v2
-  // ---------------------------------------------------------------------------
+    // binding schema v1 (legacy) -> attempt to migrate to v2
+    // ---------------------------------------------------------------------------
+
+    const targetBoundElement =
+      (targetElementsMap.get(binding.elementId) as ExcalidrawBindableElement) ||
+      undefined;
+    const boundElement =
+      targetBoundElement ||
+      (existingElementsMap?.get(
+        binding.elementId,
+      ) as ExcalidrawBindableElement) ||
+      undefined;
+    const elementsMap = targetBoundElement
+      ? targetElementsMap
+      : existingElementsMap;
+
+    // migrating legacy focus point bindings
+    if (boundElement && elementsMap) {
+      const p = LinearElementEditor.getPointAtIndexGlobalCoordinates(
+        element,
+        startOrEnd === "start" ? 0 : element.points.length - 1,
+        elementsMap,
+      );
+      const mode = isPointInElement(p, boundElement, elementsMap)
+        ? "inside"
+        : "orbit";
+      const focusPoint =
+        mode === "inside"
+          ? p
+          : projectFixedPointOntoDiagonal(
+              element,
+              p,
+              boundElement,
+              startOrEnd,
+              elementsMap,
+            ) || p;
+      const { fixedPoint } = calculateFixedPointForNonElbowArrowBinding(
+        element,
+        boundElement,
+        startOrEnd,
+        elementsMap,
+        focusPoint,
+      );

-  if (binding.mode) {
-    // if latest binding schema, don't check if binding.elementId exists
-    // (it's done in a separate pass)
-    if (binding.elementId) {
       return {
+        mode,
         elementId: binding.elementId,
-        mode: binding.mode,
-        fixedPoint: normalizeFixedPoint(binding.fixedPoint || [0.5, 0.5]),
-      } as FixedPointBinding | null;
+        fixedPoint,
+      };
     }
-    return null;
-  }
-
-  // binding schema v1 (legacy) -> attempt to migrate to v2
-  // ---------------------------------------------------------------------------
-
-  const targetBoundElement =
-    (targetElementsMap.get(binding.elementId) as ExcalidrawBindableElement) ||
-    undefined;
-  const boundElement =
-    targetBoundElement ||
-    (existingElementsMap?.get(
-      binding.elementId,
-    ) as ExcalidrawBindableElement) ||
-    undefined;
-  const elementsMap = targetBoundElement
-    ? targetElementsMap
-    : existingElementsMap;
-
-  // migrating legacy focus point bindings
-  if (boundElement && elementsMap) {
-    const p = LinearElementEditor.getPointAtIndexGlobalCoordinates(
-      element,
-      startOrEnd === "start" ? 0 : element.points.length - 1,
-      elementsMap,
-    );
-    const mode = isPointInElement(p, boundElement, elementsMap)
-      ? "inside"
-      : "orbit";
-    const focusPoint =
-      mode === "inside"
-        ? p
-        : projectFixedPointOntoDiagonal(
-            element,
-            p,
-            boundElement,
-            startOrEnd,
-            elementsMap,
-          ) || p;
-    const { fixedPoint } = calculateFixedPointForNonElbowArrowBinding(
-      element,
-      boundElement,
-      startOrEnd,
-      elementsMap,
-      focusPoint,
-    );

-    return {
-      mode,
-      elementId: binding.elementId,
-      fixedPoint,
-    };
+    console.error(`could not repair binding for element`);
+  } catch (error) {
+    console.error("Error repairing binding:", error);
   }

-  console.error(`could not repair binding for element`);
-
   return null;
 };

@@ -639,15 +643,20 @@ export const restoreElements = <T extends ExcalidrawElement>(
       if (element.type === "selection") {
         return elements;
       }
-
-      let migratedElement: ExcalidrawElement | null = restoreElement(
-        element,
-        targetElementsMap,
-        existingElementsMap,
-        {
-          deleteInvisibleElements: opts?.deleteInvisibleElements,
-        },
-      );
+      let migratedElement: ExcalidrawElement | null;
+      try {
+        migratedElement = restoreElement(
+          element,
+          targetElementsMap,
+          existingElementsMap,
+          {
+            deleteInvisibleElements: opts?.deleteInvisibleElements,
+          },
+        );
+      } catch (error) {
+        console.error("Error restoring element:", error);
+        migratedElement = null;
+      }
       if (migratedElement) {
         const localElement = existingElementsMap?.get(element.id);
PATCH

echo "Patch applied successfully"
