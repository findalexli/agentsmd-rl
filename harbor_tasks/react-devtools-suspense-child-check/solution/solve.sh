#!/bin/bash
set -euo pipefail

# Idempotent fix application for React DevTools suspense child check

STORE_FILE="/workspace/react/packages/react-devtools-shared/src/devtools/store.js"

# Check if already applied - use the NEW error message's distinctive phrase
# (base commit already has "Cannot remove suspense node" for a different check)
if grep -q "is not a child of the parent" "${STORE_FILE}" 2>/dev/null; then
    echo "Fix already applied (child-of-parent check found)"
    exit 0
fi

# Apply the fix using git apply
cd /workspace/react

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/store.js b/packages/react-devtools-shared/src/devtools/store.js
index cb3bdccdec28..5466e798aad4 100644
--- a/packages/react-devtools-shared/src/devtools/store.js
+++ b/packages/react-devtools-shared/src/devtools/store.js
@@ -1873,6 +1873,13 @@ export default class Store extends EventEmitter<{
               }

               const index = parentSuspense.children.indexOf(id);
+              if (index === -1) {
+                this._throwAndEmitError(
+                  Error(
+                    `Cannot remove suspense node "${id}" from parent "${parentID}" because it is not a child of the parent.`,
+                  ),
+                );
+              }
               parentSuspense.children.splice(index, 1);
             }
           }
PATCH

echo "Fix applied successfully"
