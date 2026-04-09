#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'initializedChunk.reason = null;' packages/react-client/src/ReactFlightClient.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index 098a1a687e3a..fa89cf69ad67 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -1040,6 +1040,8 @@ function initializeModelChunk<T>(chunk: ResolvedModelChunk<T>): void {
     // Initialize any debug info and block the initializing chunk on any
     // unresolved entries.
     initializeDebugChunk(response, chunk);
+    // TODO: The chunk might have transitioned to ERRORED now.
+    // Should we return early if that happens?
   }

   try {
@@ -1075,6 +1077,7 @@ function initializeModelChunk<T>(chunk: ResolvedModelChunk<T>): void {
     const initializedChunk: InitializedChunk<T> = (chunk: any);
     initializedChunk.status = INITIALIZED;
     initializedChunk.value = value;
+    initializedChunk.reason = null;

     if (__DEV__) {
       processChunkDebugInfo(response, initializedChunk, value);
@@ -1097,6 +1100,7 @@ function initializeModuleChunk<T>(chunk: ResolvedModuleChunk<T>): void {
     const initializedChunk: InitializedChunk<T> = (chunk: any);
     initializedChunk.status = INITIALIZED;
     initializedChunk.value = value;
+    initializedChunk.reason = null;
   } catch (error) {
     const erroredChunk: ErroredChunk<T> = (chunk: any);
     erroredChunk.status = ERRORED;
diff --git a/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js b/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js
index 94a5ac94546a..4abc18843050 100644
--- a/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js
+++ b/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js
@@ -1418,6 +1418,95 @@ describe('ReactFlightDOM', () => {
     expect(reportedErrors).toEqual([]);
   });

+  it('should not retain stale error reason after reentrant module chunk initialization', async () => {
+    function MyComponent() {
+      return <div>hello from client component</div>;
+    }
+    const ClientComponent = clientExports(MyComponent);
+
+    let resolveAsyncComponent;
+    async function AsyncComponent() {
+      await new Promise(r => {
+        resolveAsyncComponent = r;
+      });
+      return null;
+    }
+
+    function ServerComponent() {
+      return (
+        <>
+          <ClientComponent />
+          <Suspense>
+            <AsyncComponent />
+          </Suspense>
+        </>
+      );
+    }
+
+    const {writable: flightWritable, readable: flightReadable} =
+      getTestStream();
+    const {writable: fizzWritable, readable: fizzReadable} = getTestStream();
+
+    const {pipe} = await serverAct(() =>
+      ReactServerDOMServer.renderToPipeableStream(
+        <ServerComponent />,
+        webpackMap,
+      ),
+    );
+    pipe(flightWritable);
+
+    let response = null;
+    function getResponse() {
+      if (response === null) {
+        response =
+          ReactServerDOMClient.createFromReadableStream(flightReadable);
+      }
+      return response;
+    }
+
+    // Simulate a module that calls captureOwnerStack() during evaluation.
+    // In Fizz SSR, this causes a reentrant readChunk on the same module chunk.
+    // The reentrant require throws a TDZ error.
+    let evaluatingModuleId = null;
+    const origRequire = global.__webpack_require__;
+    global.__webpack_require__ = function (id) {
+      if (id === evaluatingModuleId) {
+        throw new ReferenceError(
+          "Cannot access 'MyComponent' before initialization",
+        );
+      }
+      const result = origRequire(id);
+      if (result === MyComponent) {
+        evaluatingModuleId = id;
+        if (__DEV__) {
+          React.captureOwnerStack();
+        }
+        evaluatingModuleId = null;
+      }
+      return result;
+    };
+
+    function App() {
+      return use(getResponse());
+    }
+
+    await serverAct(async () => {
+      ReactDOMFizzServer.renderToPipeableStream(<App />).pipe(fizzWritable);
+    });
+
+    global.__webpack_require__ = origRequire;
+
+    // Resolve the async component so the Flight stream closes after the client
+    // module chunk was initialized.
+    await serverAct(async () => {
+      resolveAsyncComponent();
+    });
+
+    const container = document.createElement('div');
+    await readInto(container, fizzReadable);
+    expect(container.innerHTML).toContain('hello from client component');
+  });
+
   it('should be able to recover from a direct reference erroring server-side', async () => {
     const reportedErrors = [];

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

echo "Patch applied successfully."
