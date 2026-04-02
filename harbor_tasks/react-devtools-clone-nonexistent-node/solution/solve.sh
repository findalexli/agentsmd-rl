#!/bin/bash
set -euo pipefail

cd /workspace/react
# Check if already applied
target_file="packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js"
if grep -q "Could not clone the node" "$target_file"; then
    echo "Patch already applied"
    exit 0
fi

echo "Applying fix..."
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js b/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js
index 41c5c7a2c098..9a2c3fa3056c 100644
--- a/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js
+++ b/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js
@@ -160,11 +160,14 @@ function updateTree(

   // Clone nodes before mutating them so edits don't affect them.
   const getClonedNode = (id: number): CommitTreeNode => {
-    // $FlowFixMe[prop-missing] - recommended fix is to use object spread operator
-    const clonedNode = ((Object.assign(
-      {},
-      nodes.get(id),
-    ): any): CommitTreeNode);
+    const existingNode = nodes.get(id);
+    if (existingNode == null) {
+      throw new Error(
+        `Could not clone the node: commit tree does not contain fiber "${id}". This is a bug in React DevTools.`,
+      );
+    }
+
+    const clonedNode = {...existingNode};
     nodes.set(id, clonedNode);
     return clonedNode;
   };
PATCH

echo "Fix applied successfully"
