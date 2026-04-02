#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'primaryChildFragment.sibling' packages/react-reconciler/src/ReactFiberNewContext.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/ReactFiberNewContext.js b/packages/react-reconciler/src/ReactFiberNewContext.js
index 193cf74d3bec..ac9d766d6ae3 100644
--- a/packages/react-reconciler/src/ReactFiberNewContext.js
+++ b/packages/react-reconciler/src/ReactFiberNewContext.js
@@ -323,12 +323,23 @@ function propagateContextChanges<T>(
         renderLanes,
         workInProgress,
       );
-      if (!forcePropagateEntireTree) {
-        // During lazy propagation, we can defer propagating changes to
-        // the children, same as the consumer match above.
-        nextFiber = null;
+      // The primary children's fibers may not exist in the tree (they
+      // were discarded on initial mount if they suspended). However, the
+      // fallback children ARE in the committed tree and visible to the
+      // user. We need to continue propagating into the fallback subtree
+      // so that its context consumers are marked for re-render.
+      //
+      // The fiber structure is:
+      //   SuspenseComponent
+      //     → child: OffscreenComponent (primary, hidden)
+      //       → sibling: FallbackFragment
+      //
+      // Skip the primary (hidden) subtree and jump to the fallback.
+      const primaryChildFragment = fiber.child;
+      if (primaryChildFragment !== null) {
+        nextFiber = primaryChildFragment.sibling;
       } else {
-        nextFiber = fiber.child;
+        nextFiber = null;
       }
     } else {
       // Traverse down.

PATCH

echo "Patch applied successfully."
