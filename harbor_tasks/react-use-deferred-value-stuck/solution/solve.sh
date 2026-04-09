#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'record the pinged lanes so markRootSuspended' packages/react-reconciler/src/ReactFiberWorkLoop.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/ReactFiberWorkLoop.js b/packages/react-reconciler/src/ReactFiberWorkLoop.js
index 15a260bc660c..6eed36e6d878 100644
--- a/packages/react-reconciler/src/ReactFiberWorkLoop.js
+++ b/packages/react-reconciler/src/ReactFiberWorkLoop.js
@@ -5040,6 +5040,13 @@ function pingSuspendedRoot(
         // the special internal exception that we use to interrupt the stack for
         // selective hydration. That was temporarily reverted but we once we add
         // it back we can use it here.
+        //
+        // In the meantime, record the pinged lanes so markRootSuspended won't
+        // mark them as suspended, allowing a retry.
+        workInProgressRootPingedLanes = mergeLanes(
+          workInProgressRootPingedLanes,
+          pingedLanes,
+        );
       }
     } else {
       // Even though we can't restart right now, we might get an

PATCH

echo "Patch applied successfully."
