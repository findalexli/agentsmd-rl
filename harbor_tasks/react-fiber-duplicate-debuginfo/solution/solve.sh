#!/bin/bash
set -euo pipefail

# Check if fix is already applied (look for the comment added in the fix)
if grep -q "We created a Fragment for this child with the debug info" packages/react-reconciler/src/ReactChildFiber.js; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the fix
git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/ReactChildFiber.js b/packages/react-reconciler/src/ReactChildFiber.js
index 2a726447263c..42f1b70918d3 100644
--- a/packages/react-reconciler/src/ReactChildFiber.js
+++ b/packages/react-reconciler/src/ReactChildFiber.js
@@ -789,6 +789,7 @@ function createChildReconciler(
           // We treat the parent as the owner for stack purposes.
           created._debugOwner = returnFiber;
           created._debugTask = returnFiber._debugTask;
+          // Make sure to not push again when handling the Fragment child.
           const prevDebugInfo = pushDebugInfo(newChild._debugInfo);
           created._debugInfo = currentDebugInfo;
           currentDebugInfo = prevDebugInfo;
@@ -1915,26 +1916,26 @@ function createChildReconciler(
       }

       if (isArray(newChild)) {
-        const prevDebugInfo = pushDebugInfo(newChild._debugInfo);
+        // We created a Fragment for this child with the debug info.
+        // No need to push again.
         const firstChild = reconcileChildrenArray(
           returnFiber,
           currentFirstChild,
           newChild,
           lanes,
         );
-        currentDebugInfo = prevDebugInfo;
         return firstChild;
       }

       if (getIteratorFn(newChild)) {
-        const prevDebugInfo = pushDebugInfo(newChild._debugInfo);
+        // We created a Fragment for this child with the debug info.
+        // No need to push again.
         const firstChild = reconcileChildrenIteratable(
           returnFiber,
           currentFirstChild,
           newChild,
           lanes,
         );
-        currentDebugInfo = prevDebugInfo;
         return firstChild;
       }

@@ -1942,14 +1943,14 @@ function createChildReconciler(
         enableAsyncIterableChildren &&
         typeof newChild[ASYNC_ITERATOR] === 'function'
       ) {
-        const prevDebugInfo = pushDebugInfo(newChild._debugInfo);
+        // We created a Fragment for this child with the debug info.
+        // No need to push again.
         const firstChild = reconcileChildrenAsyncIteratable(
           returnFiber,
           currentFirstChild,
           newChild,
           lanes,
         );
-        currentDebugInfo = prevDebugInfo;
         return firstChild;
       }
PATCH

echo "Fix applied successfully"
