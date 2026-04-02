#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied (idempotency check)
if grep -q "Nothing suspended the initial paint." packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js b/packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js
index 78c137deaf37..50186f47b215 100644
--- a/packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js
+++ b/packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js
@@ -36,6 +36,7 @@ import {
   UNKNOWN_SUSPENDERS_REASON_OLD_VERSION,
   UNKNOWN_SUSPENDERS_REASON_THROWN_PROMISE,
 } from '../../../constants';
+import {ElementTypeRoot} from 'react-devtools-shared/src/frontend/types';

 type RowProps = {
   bridge: FrontendBridge,
@@ -477,7 +478,21 @@ export default function InspectedElementSuspendedBy({
         </div>
       );
     }
-    return null;
+    // For roots, show an empty state since there's nothing else to show for
+    // these elements.
+    // This can happen for older versions of React without Suspense, older versions
+    // of React with less sources for Suspense, or simple UIs that don't have any suspenders.
+    if (inspectedElement.type === ElementTypeRoot) {
+      return (
+        <div>
+          <div className={styles.HeaderRow}>
+            <div className={`${styles.Header} ${styles.Empty}`}>
+              Nothing suspended the initial paint.
+            </div>
+          </div>
+        </div>
+      );
+    }
   }

   const handleCopy = withPermissionsCheck((PATCH

echo "Patch applied successfully."
