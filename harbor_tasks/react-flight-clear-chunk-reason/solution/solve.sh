#!/bin/bash
set -euo pipefail

# Check if fix is already applied
if grep -q "initializedChunk.reason = null" packages/react-client/src/ReactFlightClient.js; then
    echo "Fix already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index 098a1a687e3a..fa89cf69ad67 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -1075,6 +1075,7 @@ function initializeModelChunk<T>(chunk: ResolvedModelChunk<T>): void {
     const initializedChunk: InitializedChunk<T> = (chunk: any);
     initializedChunk.status = INITIALIZED;
     initializedChunk.value = value;
+    initializedChunk.reason = null;

     if (__DEV__) {
       processChunkDebugInfo(response, initializedChunk, value);
@@ -1097,6 +1098,7 @@ function initializeModuleChunk<T>(chunk: ResolvedModuleChunk<T>): void {
     const initializedChunk: InitializedChunk<T> = (chunk: any);
     initializedChunk.status = INITIALIZED;
     initializedChunk.value = value;
+    initializedChunk.reason = null;
   } catch (error) {
     const erroredChunk: ErroredChunk<T> = (chunk: any);
     erroredChunk.status = ERRORED;
diff --git a/packages/react-server/src/ReactFlightReplyServer.js b/packages/react-server/src/ReactFlightReplyServer.js
index d3eff13ff465..21ff08a8aa02 100644
--- a/packages/react-server/src/ReactFlightReplyServer.js
+++ b/packages/react-server/src/ReactFlightReplyServer.js
@@ -478,6 +478,7 @@ function loadServerReference<A: Iterable<any>, T>(
       const initializedPromise: InitializedChunk<T> = (blockedPromise: any);
       initializedPromise.status = INITIALIZED;
       initializedPromise.value = resolvedValue;
+      initializedPromise.reason = null;
       return resolvedValue;
     }
   } else if (bound instanceof ReactPromise) {
PATCH

echo "Fix applied successfully"
