#!/bin/bash
set -euo pipefail

# React DevTools: Allow renaming Host Component props
# Fixes crash when renaming props on Host Components (e.g., <input>) by only
# using forceUpdate() for Class Components, not Host Components.

REPO_ROOT="/workspace/react"
TARGET_FILE="packages/react-devtools-shared/src/backend/fiber/renderer.js"

# Check if already applied - look for the ClassComponent switch case
if grep -q "case ClassComponent:" "${REPO_ROOT}/${TARGET_FILE}"; then
    echo "Fix already applied (ClassComponent switch case found)"
    exit 0
fi

# Apply the patch
cd "${REPO_ROOT}"

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 61c6f86dd6b4..5a977dc762bb 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -7874,17 +7874,20 @@ export function attach(
           }
           break;
         case 'props':
-          if (instance === null) {
-            if (typeof overridePropsRenamePath === 'function') {
-              overridePropsRenamePath(fiber, oldPath, newPath);
-            }
-          } else {
-            fiber.pendingProps = copyWithRename(
-              instance.props,
-              oldPath,
-              newPath,
-            );
-            instance.forceUpdate();
+          switch (fiber.tag) {
+            case ClassComponent:
+              fiber.pendingProps = copyWithRename(
+                instance.props,
+                oldPath,
+                newPath,
+              );
+              instance.forceUpdate();
+              break;
+            default:
+              if (typeof overridePropsRenamePath === 'function') {
+                overridePropsRenamePath(fiber, oldPath, newPath);
+              }
+              break;
           }
           break;
         case 'state':
PATCH

echo "Fix applied successfully"
