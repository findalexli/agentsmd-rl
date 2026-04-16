#!/bin/bash
set -e

# Navigate to the expo package directory
cd /workspace/expo/packages/expo

# Apply the fix patch
cat > /tmp/fix.patch << 'PATCH'
diff --git a/packages/expo/src/winter/installGlobal.ts b/packages/expo/src/winter/installGlobal.ts
index ffb42bc1c42eaa..2f81a36e3e0f15 100644
--- a/packages/expo/src/winter/installGlobal.ts
+++ b/packages/expo/src/winter/installGlobal.ts
@@ -81,9 +81,14 @@ export function installGlobal<T extends object>(name: string, getValue: () => T)
   // @ts-ignore: globalThis is not defined in all environments
   const object = typeof global !== 'undefined' ? global : globalThis;
   const descriptor = Object.getOwnPropertyDescriptor(object, name);
-  if (__DEV__ && descriptor) {
+
+  // NOTE(@kitten): We have to exclude descriptors with getters here
+  // When two calls of a "lazy getter" conflict, accessing the original will override the global again
+  // (e.g. `globalThis.originalURL` in react-native will set URL back to its own value)
+  if (__DEV__ && descriptor && !descriptor.get) {
     const backupName = `original${name[0] ?? ''.toUpperCase()}${name.slice(1)}`;
-    Object.defineProperty(object, backupName, descriptor);
+    // NOTE(@kitten): We don't want the global to be enumerably different in development
+    Object.defineProperty(object, backupName, { ...descriptor, enumerable: false });
   }
 
   const { enumerable, writable, configurable = false } = descriptor || {};
PATCH

# Apply the patch
git apply /tmp/fix.patch

# Verify the patch was applied by checking for a distinctive line from the fix
grep -q "NOTE(@kitten): We have to exclude descriptors with getters" src/winter/installGlobal.ts && echo "Fix applied successfully"
