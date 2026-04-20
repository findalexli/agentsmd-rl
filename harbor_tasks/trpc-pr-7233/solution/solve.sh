#!/bin/bash
set -e
cd /workspace/trpc

# Apply the gold patch
git apply -- <<'PATCH'
diff --git a/packages/server/src/unstable-core-do-not-import/stream/jsonl.test.ts b/packages/server/src/unstable-core-do-not-import/stream/jsonl.test.ts
index aa10b6da42b..1094ee741c2 100644
--- a/packages/server/src/unstable-core-do-not-import/stream/jsonl.test.ts
+++ b/packages/server/src/unstable-core-do-not-import/stream/jsonl.test.ts
@@ -667,3 +667,71 @@ test('regression: encode/decode with superjson at top level', async () => {

   expect(abortController.signal.aborted).toBe(true);
 });
+
+// https://github.com/trpc/trpc/issues/7209
+test('regression: buffered chunks preserved on normal stream completion', async () => {
+  const abortController = new AbortController();
+  const data = {
+    0: Promise.resolve({
+      [Symbol.asyncIterator]: async function* () {
+        // Yield multiple values quickly so they buffer in the ReadableStream
+        for (let i = 0; i < 5; i++) {
+          yield i;
+        }
+      },
+    }),
+  } as const;
+  const stream = jsonlStreamProducer({
+    data,
+    serialize: (v) => SuperJSON.serialize(v),
+  });
+
+  const [head] = await jsonlStreamConsumer<typeof data>({
+    from: stream,
+    deserialize: (v) => SuperJSON.deserialize(v),
+    abortController,
+  });
+
+  const iterable = await head[0];
+
+  // Consume values with a slow reader so that the pipeTo pipeline completes
+  // (including its close/abort callback) while chunks are still buffered.
+  // Without the fix, the close handler calls controller.error() which discards
+  // buffered chunks; with the fix it calls controller.close() preserving them.
+  const values: number[] = [];
+  for await (const item of iterable) {
+    values.push(item);
+
+    // Yield to the event loop so pipeTo can finish and fire close/abort
+    await new Promise((r) => setTimeout(r, 10));
+  }
+
+  // All buffered chunks should be delivered on normal completion
+  expect(values).toEqual([0, 1, 2, 3, 4]);
+  expect(abortController.signal.aborted).toBe(true);
+});
+
+// https://github.com/trpc/trpc/issues/7209
+test('regression: stream closing before head rejects headDeferred with descriptive error', async () => {
+  const abortController = new AbortController();
+
+  // Create a ReadableStream that closes immediately with no data
+  const emptyStream = new ReadableStream<Uint8Array>({
+    start(controller) {
+      controller.close();
+    },
+  });
+
+  const rejection = await jsonlStreamConsumer({
+    from: emptyStream,
+    abortController,
+  }).catch((e) => e);
+
+  // Without the fix, close calls closeOrAbort(undefined) which rejects with undefined.
+  // With the fix, handleClose rejects with a descriptive Error.
+  expect(rejection).toBeInstanceOf(Error);
+  expect(rejection).toHaveProperty(
+    'message',
+    'Stream closed before head was received',
+  );
+});
diff --git a/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts b/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts
index 3013ad54313..ef2d1954073 100644
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