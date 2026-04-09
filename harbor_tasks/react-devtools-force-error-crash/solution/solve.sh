#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'boolean | null' packages/react-devtools-shared/src/backend/fiber/renderer.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 49e6192b467e..aa7fe9d6ee84 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -7898,7 +7898,7 @@ export function attach(
   // Map of Fiber and its force error status: true (error), false (toggled off)
   const forceErrorForFibers = new Map<Fiber, boolean>();

-  function shouldErrorFiberAccordingToMap(fiber: any): boolean {
+  function shouldErrorFiberAccordingToMap(fiber: any): boolean | null {
     if (typeof setErrorHandler !== 'function') {
       throw new Error(
         'Expected overrideError() to not get called for earlier React versions.',
@@ -7934,7 +7934,7 @@ export function attach(
       }
     }
     if (status === undefined) {
-      return false;
+      return null;
     }
     return status;
   }
diff --git a/packages/react-reconciler/src/ReactFiberBeginWork.js b/packages/react-reconciler/src/ReactFiberBeginWork.js
index 49a4c53c8941..cf2c08236733 100644
--- a/packages/react-reconciler/src/ReactFiberBeginWork.js
+++ b/packages/react-reconciler/src/ReactFiberBeginWork.js
@@ -1584,6 +1584,9 @@ function updateClassComponent(
     // This is used by DevTools to force a boundary to error.
     switch (shouldError(workInProgress)) {
       case false: {
+        // We previously simulated an error on this boundary
+        // so the instance must have been constructed in a previous
+        // commit.
         const instance = workInProgress.stateNode;
         const ctor = workInProgress.type;
         // TODO This way of resetting the error boundary state is a hack.

PATCH

echo "Patch applied successfully."
