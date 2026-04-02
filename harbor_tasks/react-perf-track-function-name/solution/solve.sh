#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
grep -q "typeof functionName !== 'string'" packages/shared/ReactPerformanceTrackProperties.js 2>/dev/null && {
    echo "Patch already applied."
    exit 0
}

git apply - <<'PATCH'
diff --git a/packages/shared/ReactPerformanceTrackProperties.js b/packages/shared/ReactPerformanceTrackProperties.js
index a2063584bdf0..3bca2fac60fd 100644
--- a/packages/shared/ReactPerformanceTrackProperties.js
+++ b/packages/shared/ReactPerformanceTrackProperties.js
@@ -253,10 +253,15 @@ export function addValueToProperties(
         return;
       }
     case 'function':
-      if (value.name === '') {
+      const functionName = value.name;
+      if (
+        functionName === '' ||
+        // e.g. proxied functions or classes with a static property "name" that's not a string
+        typeof functionName !== 'string'
+      ) {
         desc = '() => {}';
       } else {
-        desc = value.name + '() {}';
+        desc = functionName + '() {}';
       }
       break;
     case 'string':
PATCH

echo "Patch applied successfully."
