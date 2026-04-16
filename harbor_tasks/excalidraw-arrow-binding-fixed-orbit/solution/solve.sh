#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if grep -q "const otherNeverOverride = opts?.newArrow" packages/element/src/binding.ts; then
    echo "Fix already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/element/src/binding.ts b/packages/element/src/binding.ts
index 074fe2a21ffa..0093a110646f 100644
--- a/packages/element/src/binding.ts
+++ b/packages/element/src/binding.ts
@@ -810,10 +810,13 @@ const getBindingStrategyForDraggingBindingElementEndpoints_simple = (
     elementsMap,
   );

-  const other: BindingStrategy =
-    otherBindableElement &&
-    !otherFocusPointIsInElement &&
-    appState.selectedLinearElement?.initialState.altFocusPoint
+  const otherNeverOverride = opts?.newArrow
+    ? appState.selectedLinearElement?.initialState.arrowStartIsInside
+    : otherBinding?.mode === "inside";
+  const other: BindingStrategy = !otherNeverOverride
+    ? otherBindableElement &&
+      !otherFocusPointIsInElement &&
+      appState.selectedLinearElement?.initialState.altFocusPoint
       ? {
           mode: "orbit",
           element: otherBindableElement,
@@ -832,7 +835,8 @@ const getBindingStrategyForDraggingBindingElementEndpoints_simple = (
               elementsMap,
             ) || otherEndpoint,
         }
-      : { mode: undefined };
+      : { mode: undefined }
+    : { mode: undefined };

   return {
     start: startDragged ? current : other,
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index fa9a02b492b2..88871adde241 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -8743,6 +8743,7 @@ class App extends React.Component<AppProps, AppState> {
               selectedPointsIndices: [endIdx],
               initialState: {
                 ...linearElementEditor.initialState,
+                arrowStartIsInside: event.altKey,
                 lastClickedPoint: endIdx,
                 origin: pointFrom<GlobalPoint>(
                   pointerDownState.origin.x,
PATCH

echo "Fix applied successfully"
