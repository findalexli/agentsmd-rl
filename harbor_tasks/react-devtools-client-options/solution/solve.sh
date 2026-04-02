#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if the fix is already applied
define_path_option=$(grep -c "prefixedPath" packages/react-devtools-core/src/backend.js 2>/dev/null || echo "0")
client_options_type=$(grep -c "ClientOptions" packages/react-devtools-core/src/standalone.js 2>/dev/null || echo "0")

if [[ "$define_path_option" -gt 0 && "$client_options_type" -gt 0 ]]; then
    echo "Fix already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-core/src/backend.js b/packages/react-devtools-core/src/backend.js
index 262b3bc04127..075758f78500 100644
--- a/packages/react-devtools-core/src/backend.js
+++ b/packages/react-devtools-core/src/backend.js
@@ -33,6 +33,7 @@ import type {ResolveNativeStyle} from 'react-devtools-shared/src/backend/NativeS
 type ConnectOptions = {
   host?: string,
   nativeStyleEditorValidAttributes?: $ReadOnlyArray<string>,
+  path?: string,
   port?: number,
   useHttps?: boolean,
   resolveRNStyle?: ResolveNativeStyle,
@@ -93,6 +94,7 @@ export function connectToDevTools(options: ?ConnectOptions) {
   const {
     host = 'localhost',
     nativeStyleEditorValidAttributes,
+    path = '',
     useHttps = false,
     port = 8097,
     websocket,
@@ -107,6 +109,7 @@ export function connectToDevTools(options: ?ConnectOptions) {
   } = options || {};

   const protocol = useHttps ? 'wss' : 'ws';
+  const prefixedPath = path !== '' && !path.startsWith('/') ? '/' + path : path;
   let retryTimeoutID: TimeoutID | null = null;

   function scheduleRetry() {
@@ -129,7 +132,7 @@ export function connectToDevTools(options: ?ConnectOptions) {
   let bridge: BackendBridge | null = null;

   const messageListeners = [];
-  const uri = protocol + '://' + host + ':' + port;
+  const uri = protocol + '://' + host + ':' + port + prefixedPath;

   // If existing websocket is passed, use it.
   // This is necessary to support our custom integrations.
diff --git a/packages/react-devtools-core/src/standalone.js b/packages/react-devtools-core/src/standalone.js
index df89a728c308..2a154458154b 100644
--- a/packages/react-devtools-core/src/standalone.js
+++ b/packages/react-devtools-core/src/standalone.js
@@ -306,11 +306,19 @@ type LoggerOptions = {
   surface?: ?string,
 };

+type ClientOptions = {
+  host?: string,
+  port?: number,
+  useHttps?: boolean,
+};
+
 function startServer(
   port: number = 8097,
   host: string = 'localhost',
   httpsOptions?: ServerOptions,
   loggerOptions?: LoggerOptions,
+  path?: string,
+  clientOptions?: ClientOptions,
 ): {close(): void} {
   registerDevToolsEventLogger(loggerOptions?.surface ?? 'standalone');

@@ -345,7 +353,18 @@ function startServer(
   server.on('error', (event: $FlowFixMe) => {
     onError(event);
     log.error('Failed to start the DevTools server', event);
-    startServerTimeoutID = setTimeout(() => startServer(port), 1000);
+    startServerTimeoutID = setTimeout(
+      () =>
+        startServer(
+          port,
+          host,
+          httpsOptions,
+          loggerOptions,
+          path,
+          clientOptions,
+        ),
+      1000,
+    );
   });

   httpServer.on('request', (request: $FlowFixMe, response: $FlowFixMe) => {
@@ -358,14 +377,20 @@ function startServer(
     // This will ensure that saved filters are shared across different web pages.
     const componentFiltersString = JSON.stringify(getSavedComponentFilters());

+    // Client overrides: when connecting through a reverse proxy, the client
+    // may need to connect to a different host/port/protocol than the server.
+    const clientHost = clientOptions?.host ?? host;
+    const clientPort = clientOptions?.port ?? port;
+    const clientUseHttps = clientOptions?.useHttps ?? useHttps;
+
     response.end(
       backendFile.toString() +
         '\n;' +
         `ReactDevToolsBackend.initialize(undefined, undefined, undefined, ${componentFiltersString});` +
         '\n' +
-        `ReactDevToolsBackend.connectToDevTools({port: ${port}, host: '${host}', useHttps: ${
-          useHttps ? 'true' : 'false'
-        }});
+        `ReactDevToolsBackend.connectToDevTools({port: ${clientPort}, host: '${clientHost}', useHttps: ${
+          clientUseHttps ? 'true' : 'false'
+        }${path != null ? `, path: '${path}'` : ''}});
         `,
     );
   });
@@ -373,7 +398,18 @@ function startServer(
   httpServer.on('error', (event: $FlowFixMe) => {
     onError(event);
     statusListener('Failed to start the server.', 'error');
-    startServerTimeoutID = setTimeout(() => startServer(port), 1000);
+    startServerTimeoutID = setTimeout(
+      () =>
+        startServer(
+          port,
+          host,
+          httpsOptions,
+          loggerOptions,
+          path,
+          clientOptions,
+        ),
+      1000,
+    );
   });

   httpServer.listen(port, () => {
PATCH

echo "Fix applied successfully."
