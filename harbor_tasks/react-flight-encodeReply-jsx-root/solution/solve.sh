#!/usr/bin/env bash
set -euo pipefail
cd /workspace/react

# Idempotent: skip if already applied
grep -q 'modelRoot === value' packages/react-client/src/ReactFlightReplyClient.js 2>/dev/null && exit 0

git apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index 12c9528b8de6..80673006eadb 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -552,7 +552,7 @@ function moveDebugInfoFromChunkToInnerValue<T>(
         resolvedValue._debugInfo,
         debugInfo,
       );
-    } else {
+    } else if (!Object.isFrozen(resolvedValue)) {
       Object.defineProperty((resolvedValue: any), '_debugInfo', {
         configurable: false,
         enumerable: false,
@@ -560,6 +560,11 @@ function moveDebugInfoFromChunkToInnerValue<T>(
         value: debugInfo,
       });
     }
+    // TODO: If the resolved value is a frozen element (e.g. a client-created
+    // element from a temporary reference, or a JSX element exported as a client
+    // reference), server debug info is currently dropped because the element
+    // can't be mutated. We should probably clone the element so each rendering
+    // context gets its own mutable copy with the correct debug info.
   }
 }

@@ -2900,7 +2905,9 @@ function addAsyncInfo(chunk: SomeChunk<any>, asyncInfo: ReactAsyncInfo): void {
     if (isArray(value._debugInfo)) {
       // $FlowFixMe[method-unbinding]
       value._debugInfo.push(asyncInfo);
-    } else {
+    } else if (!Object.isFrozen(value)) {
+      // TODO: Debug info is dropped for frozen elements. See the TODO in
+      // moveDebugInfoFromChunkToInnerValue.
       Object.defineProperty((value: any), '_debugInfo', {
         configurable: false,
         enumerable: false,
diff --git a/packages/react-client/src/ReactFlightReplyClient.js b/packages/react-client/src/ReactFlightReplyClient.js
index 0661f7824650..56f60d3623c9 100644
--- a/packages/react-client/src/ReactFlightReplyClient.js
+++ b/packages/react-client/src/ReactFlightReplyClient.js
@@ -429,6 +429,14 @@ export function processReply(
               return serializeTemporaryReferenceMarker();
             }
           }
+          // This element is the root of a serializeModel call (e.g. JSX
+          // passed directly to encodeReply, or a promise that resolved to
+          // JSX). It was already registered as a temporary reference by
+          // serializeModel so we just need to emit the marker.
+          if (temporaryReferences !== undefined && modelRoot === value) {
+            modelRoot = null;
+            return serializeTemporaryReferenceMarker();
+          }
           throw new Error(
             'React Element cannot be passed to Server Functions from the Client without a ' +
               'temporary reference set. Pass a TemporaryReferenceSet to the options.' +
PATCH
