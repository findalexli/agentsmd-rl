#!/bin/bash
set -euo pipefail

# Check if already applied - look for the specific fix pattern
if grep -q "key === REACT_OPTIMISTIC_KEY" packages/react-devtools-shared/src/backend/fiber/renderer.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 916d69823285..d58247f448f0 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -2606,7 +2606,12 @@ export function attach(

       // This check is a guard to handle a React element that has been modified
       // in such a way as to bypass the default stringification of the "key" property.
-      const keyString = key === null ? null : String(key);
+      const keyString =
+        key === null
+          ? null
+          : key === REACT_OPTIMISTIC_KEY
+            ? 'React.optimisticKey'
+            : String(key);
       const keyStringID = getStringID(keyString);

       const nameProp =
@@ -6179,7 +6184,10 @@ export function attach(
       return {
         displayName: getDisplayNameForFiber(fiber) || 'Anonymous',
         id: instance.id,
-        key: fiber.key === REACT_OPTIMISTIC_KEY ? null : fiber.key,
+        key:
+          fiber.key === REACT_OPTIMISTIC_KEY
+            ? 'React.optimisticKey'
+            : fiber.key,
         env: null,
         stack:
           fiber._debugOwner == null || fiber._debugStack == null
@@ -6195,7 +6203,7 @@ export function attach(
         key:
           componentInfo.key == null ||
           componentInfo.key === REACT_OPTIMISTIC_KEY
-            ? null
+            ? 'React.optimisticKey'
             : componentInfo.key,
         env: componentInfo.env == null ? null : componentInfo.env,
         stack:
@@ -7120,7 +7128,12 @@ export function attach(
       // Does the component have legacy context attached to it.
       hasLegacyContext,

-      key: key != null && key !== REACT_OPTIMISTIC_KEY ? key : null,
+      key:
+        key != null
+          ? key === REACT_OPTIMISTIC_KEY
+            ? 'React.optimisticKey'
+            : key
+          : null,

       type: elementType,
PATCH

echo "Patch applied successfully"
