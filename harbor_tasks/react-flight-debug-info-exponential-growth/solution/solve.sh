set -euo pipefail

# Check if already applied - look for the isInitializingDebugInfo flag
if grep -q "let isInitializingDebugInfo: boolean = false;" /workspace/react/packages/react-client/src/ReactFlightClient.js; then
    echo "Patch already applied"
    exit 0
fi

cd /workspace/react

git apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index 20aa8ce8f9a3..4c78e8b0fca0 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -943,6 +943,7 @@ type InitializationHandler = {
 };
 let initializingHandler: null | InitializationHandler = null;
 let initializingChunk: null | BlockedChunk<any> = null;
+let isInitializingDebugInfo: boolean = false;

 function initializeDebugChunk(
   response: Response,
@@ -951,6 +952,8 @@ function initializeDebugChunk(
   const debugChunk = chunk._debugChunk;
   if (debugChunk !== null) {
     const debugInfo = chunk._debugInfo;
+    const prevIsInitializingDebugInfo = isInitializingDebugInfo;
+    isInitializingDebugInfo = true;
     try {
       if (debugChunk.status === RESOLVED_MODEL) {
         // Find the index of this debug info by walking the linked list.
@@ -1015,6 +1018,8 @@ function initializeDebugChunk(
       }
     } catch (error) {
       triggerErrorOnChunk(response, chunk, error);
+    } finally {
+      isInitializingDebugInfo = prevIsInitializingDebugInfo;
     }
   }
 }
@@ -1632,7 +1637,9 @@ function fulfillReference(
       const element: any = handler.value;
       switch (key) {
         case '3':
-          transferReferencedDebugInfo(handler.chunk, fulfilledChunk);
+          if (__DEV__) {
+            transferReferencedDebugInfo(handler.chunk, fulfilledChunk);
+          }
           element.props = mappedValue;
           break;
         case '4':
@@ -1648,7 +1655,9 @@ function fulfillReference(
           }
           break;
         default:
-          transferReferencedDebugInfo(handler.chunk, fulfilledChunk);
+          if (__DEV__) {
+            transferReferencedDebugInfo(handler.chunk, fulfilledChunk);
+          }
           break;
       }
     } else if (__DEV__ && !reference.isDebug) {
@@ -2086,7 +2095,7 @@ function getOutlinedModel<T>(
                 response,
                 map,
                 path.slice(i - 1),
-                false,
+                isInitializingDebugInfo,
               );
             }
             case HALTED: {
@@ -2158,14 +2167,21 @@ function getOutlinedModel<T>(
       }

       const chunkValue = map(response, value, parentObject, key);
-      if (
-        parentObject[0] === REACT_ELEMENT_TYPE &&
-        (key === '4' || key === '5')
-      ) {
-        // If we're resolving the "owner" or "stack" slot of an Element array, we don't call
-        // transferReferencedDebugInfo because this reference is to a debug chunk.
-      } else {
-        transferReferencedDebugInfo(initializingChunk, chunk);
+      if (__DEV__) {
+        if (
+          parentObject[0] === REACT_ELEMENT_TYPE &&
+          (key === '4' || key === '5')
+        ) {
+          // If we're resolving the "owner" or "stack" slot of an Element array,
+          // we don't call transferReferencedDebugInfo because this reference is
+          // to a debug chunk.
+        } else if (isInitializingDebugInfo) {
+          // If we're resolving references as part of debug info resolution, we
+          // don't call transferReferencedDebugInfo because these references are
+          // to debug chunks.
+        } else {
+          transferReferencedDebugInfo(initializingChunk, chunk);
+        }
       }
       return chunkValue;
     case PENDING:
@@ -2177,7 +2193,7 @@ function getOutlinedModel<T>(
         response,
         map,
         path,
-        false,
+        isInitializingDebugInfo,
       );
     case HALTED: {
       // Add a dependency that will never resolve.
@@ -4264,15 +4280,21 @@ function resolveIOInfo(
 ): void {
   const chunks = response._chunks;
   let chunk = chunks.get(id);
-  if (!chunk) {
-    chunk = createResolvedModelChunk(response, model);
-    chunks.set(id, chunk);
-    initializeModelChunk(chunk);
-  } else {
-    resolveModelChunk(response, chunk, model);
-    if (chunk.status === RESOLVED_MODEL) {
+  const prevIsInitializingDebugInfo = isInitializingDebugInfo;
+  isInitializingDebugInfo = true;
+  try {
+    if (!chunk) {
+      chunk = createResolvedModelChunk(response, model);
+      chunks.set(id, chunk);
       initializeModelChunk(chunk);
+    } else {
+      resolveModelChunk(response, chunk, model);
+      if (chunk.status === RESOLVED_MODEL) {
+        initializeModelChunk(chunk);
+      }
     }
+  } finally {
+    isInitializingDebugInfo = prevIsInitializingDebugInfo;
   }
   if (chunk.status === INITIALIZED) {
     initializeIOInfo(response, chunk.value);
diff --git a/packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js b/packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js
index 336d797efb61..5107fc0bfaea 100644
--- a/packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js
+++ b/packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js
@@ -3633,4 +3633,40 @@ describe('ReactFlightAsyncDebugInfo', () => {
       `);
     }
   });
+
+  it('should not exponentially accumulate debug info on outlined debug chunks', async () => {
+    // Regression test: Each Level wraps its received `context` prop in a new
+    // object before passing it down. This creates props deduplication
+    // references to the parent's outlined chunk alongside the owner reference,
+    // giving 2 references per level to the direct parent's chunk. Without
+    // skipping transferReferencedDebugInfo during debug info resolution, this
+    // test would fail with an infinite loop detection error.
+    async function Level({depth, context}) {
+      await delay(0);
+      if (depth === 0) {
+        return <div>Hello, World!</div>;
+      }
+      const newContext = {prev: context, id: depth};
+      return ReactServer.createElement(Level, {
+        depth: depth - 1,
+        context: newContext,
+      });
+    }
+
+    const stream = ReactServerDOMServer.renderToPipeableStream(
+      ReactServer.createElement(Level, {depth: 20, context: {root: true}}),
+    );
+
+    const readable = new Stream.PassThrough(streamOptions);
+    const result = ReactServerDOMClient.createFromNodeStream(readable, {
+      moduleMap: {},
+      moduleLoading: {},
+    });
+    stream.pipe(readable);
+
+    const resolved = await result;
+    expect(resolved.type).toBe('div');
+
+    await finishLoadingStream(readable);
+  });
 });
PATCH

echo "Patch applied successfully"
