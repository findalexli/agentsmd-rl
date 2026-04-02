#!/bin/bash
set -euo pipefail

# Check if fix is already applied
if grep -q 'typeof value === '"'"'bigint'"'"'' /workspace/react/packages/shared/ReactPerformanceTrackProperties.js 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the gold patch
git -C /workspace/react apply - <<'PATCH'
diff --git a/packages/shared/ReactPerformanceTrackProperties.js b/packages/shared/ReactPerformanceTrackProperties.js
index 87231c20c49d..f088d51025b5 100644
--- a/packages/shared/ReactPerformanceTrackProperties.js
+++ b/packages/shared/ReactPerformanceTrackProperties.js
@@ -16,7 +16,7 @@ import getComponentNameFromType from './getComponentNameFromType';

 const EMPTY_ARRAY = 0;
 const COMPLEX_ARRAY = 1;
-const PRIMITIVE_ARRAY = 2; // Primitive values only
+const PRIMITIVE_ARRAY = 2; // Primitive values only that are accepted by JSON.stringify
 const ENTRIES_ARRAY = 3; // Tuple arrays of string and value (like Headers, Map, etc)

 // Showing wider objects in the devtools is not useful.
@@ -46,6 +46,8 @@ function getArrayKind(array: Object): 0 | 1 | 2 | 3 {
       return COMPLEX_ARRAY;
     } else if (kind !== EMPTY_ARRAY && kind !== PRIMITIVE_ARRAY) {
       return COMPLEX_ARRAY;
+    } else if (typeof value === 'bigint') {
+      return COMPLEX_ARRAY;
     } else {
       kind = PRIMITIVE_ARRAY;
     }
PATCH

echo "Fix applied successfully"
