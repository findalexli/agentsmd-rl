#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'Promise.withResolvers' src/workerd/server/tests/container-client/test.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/src/workerd/server/tests/container-client/README.md b/src/workerd/server/tests/container-client/README.md
index dfe9031066d..27eae8c1fe4 100644
--- a/src/workerd/server/tests/container-client/README.md
+++ b/src/workerd/server/tests/container-client/README.md
@@ -17,7 +17,7 @@ To run the tests:
 3. Remove existing containers labeled as "cf-container-client-test"

    ```shell
-   docker rm -f $(docker ps -aq --filter name=workerd-container-client-test --all)
+   docker ps -aq --filter name=workerd-container-client-test | xargs -r docker rm -f
    ```

 4. Remove existing Docker image
@@ -35,5 +35,5 @@ To run the tests:
 6. Run the test

    ```shell
-   just stream-test //src/workerd/server/tests/container-client
+   just stream-test //src/workerd/server/tests/container-client:container-client@
    ```
diff --git a/src/workerd/server/tests/container-client/test.js b/src/workerd/server/tests/container-client/test.js
index b9af91238ad..ef80a03cebf 100644
--- a/src/workerd/server/tests/container-client/test.js
+++ b/src/workerd/server/tests/container-client/test.js
@@ -247,10 +247,6 @@ export class DurableObjectExample extends DurableObject {
             throw e;
           }

-          console.info(
-            `Retrying getTcpPort(8080) for the ${i} time due to an error ${e.message}`
-          );
-          console.info(e);
           if (i === maxRetries) {
             console.error(
               `Failed to connect to container ${container.id}. Retried ${i} times`
@@ -470,21 +466,26 @@ export class DurableObjectExample extends DurableObject {
     ws.accept();

     // Listen for response
-    const messagePromise = new Promise((resolve) => {
-      ws.addEventListener(
-        'message',
-        (event) => {
-          resolve(event.data);
-        },
-        { once: true }
-      );
-    });
+    const { promise, resolve, reject } = Promise.withResolvers();
+
+    ws.addEventListener(
+      'message',
+      (event) => {
+        resolve(event.data);
+      },
+      { once: true }
+    );
+
+    const timeout = setTimeout(() => {
+      reject(new Error('Websocket message not received within 5 seconds'));
+    }, 5_000);

     // Send a test message - should go through the whole chain and come back
     ws.send('Hello through intercept!');

     // Should receive response from TestService binding with id 42
-    const response = new TextDecoder().decode(await messagePromise);
+    const response = new TextDecoder().decode(await promise);
+    clearTimeout(timeout);
     assert.strictEqual(response, 'Binding 42: Hello through intercept!');

     ws.close();

PATCH

echo "Patch applied successfully."
