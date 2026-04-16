#!/bin/bash
set -e

cd /workspace/trpc

# Apply the gold patch for PR #7233
patch -p1 << 'PATCH'
diff --git a/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts b/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts
index abc123..def456 100644
--- a/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts
+++ b/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts
@@ -493,9 +493,19 @@ function createStreamsManager(abortController: AbortController) {
     }
   }

+  /**
+   * Closes all pending controllers to preserve buffered data
+   */
+  function closeAll() {
+    for (const controller of controllerMap.values()) {
+      controller.close();
+    }
+  }
+
   return {
     getOrCreate,
     cancelAll,
+    closeAll,
   };
 }

@@ -591,8 +601,21 @@ export async function jsonlStreamConsumer<THead>(opts: {
     return data;
   }

-  const closeOrAbort = (reason?: unknown) => {
+  const handleClose = () => {
+    // If the stream closes before emitting any head data,
+    // we need to reject the headDeferred to prevent hanging
+    if (headDeferred) {
+      headDeferred.reject(new Error('Stream closed before head was received'));
+      headDeferred = null;
+    }
+    // Close stream controllers (not error them)
+    // to preserve any buffered chunks
+    streamManager.closeAll();
+  };
+
+  const handleAbort = (reason?: unknown) => {
     headDeferred?.reject(reason);
+    headDeferred = null;
     streamManager.cancelAll(reason);
   };

@@ -618,13 +641,13 @@ export async function jsonlStreamConsumer<THead>(opts: {
           const controller = streamManager.getOrCreate(idx);
           controller.enqueue(chunk);
         },
-        close: closeOrAbort,
-        abort: closeOrAbort,
+        close: handleClose,
+        abort: handleAbort,
       }),
     )
     .catch((error) => {
       opts.onError?.({ error });
-      closeOrAbort(error);
+      handleAbort(error);
     });

   return [await headDeferred.promise] as const;
PATCH

# Verify the distinctive line was applied
grep -q "Stream closed before head was received" packages/server/src/unstable-core-do-not-import/stream/jsonl.ts

echo "Patch applied successfully"
