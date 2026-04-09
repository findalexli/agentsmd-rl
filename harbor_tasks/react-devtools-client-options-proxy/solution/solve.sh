#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'clientOptions' packages/react-devtools-core/src/standalone.js 2>/dev/null; then
    echo "Patch already applied."
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
diff --git a/packages/react-devtools/app.html b/packages/react-devtools/app.html
index 7b55e0d37db9..1d11394c9427 100644
--- a/packages/react-devtools/app.html
+++ b/packages/react-devtools/app.html
@@ -158,12 +158,19 @@
     <script>
       // window.api is defined in preload.js
       const {electron, readEnv, ip, getDevTools} = window.api;
-      const {options, useHttps, host, protocol, port} = readEnv();
+      const {options, useHttps, host, protocol, port, path, clientHost, clientPort, clientUseHttps} = readEnv();

       const localIp = ip.address();
-      const defaultPort = (port === 443 && useHttps) || (port === 80 && !useHttps);
-      const server = defaultPort ? `${protocol}://${host}` : `${protocol}://${host}:${port}`;
-      const serverIp = defaultPort ? `${protocol}://${localIp}` : `${protocol}://${localIp}:${port}`;
+
+      // Effective values for display URLs: client overrides take precedence over server values.
+      const effectiveHost = clientHost != null ? clientHost : host;
+      const effectivePort = clientPort != null ? clientPort : port;
+      const effectiveUseHttps = clientUseHttps != null ? clientUseHttps : useHttps;
+      const effectiveProtocol = effectiveUseHttps ? 'https' : 'http';
+      const defaultPort = (effectivePort === 443 && effectiveUseHttps) || (effectivePort === 80 && !effectiveUseHttps);
+      const pathStr = path != null ? path : '';
+      const server = defaultPort ? `${effectiveProtocol}://${effectiveHost}${pathStr}` : `${effectiveProtocol}://${effectiveHost}:${effectivePort}${pathStr}`;
+      const serverIp = defaultPort ? `${effectiveProtocol}://${localIp}${pathStr}` : `${effectiveProtocol}://${localIp}:${effectivePort}${pathStr}`;
       const $ = document.querySelector.bind(document);

       let timeoutID;
@@ -234,7 +241,7 @@
             element.innerText = status;
           }
         })
-        .startServer(port, host, options);
+        .startServer(port, host, options, undefined, path, {host: clientHost, port: clientPort, useHttps: clientUseHttps});
     </script>
   </body>
 </html>
diff --git a/packages/react-devtools/preload.js b/packages/react-devtools/preload.js
index 33a9e3d6dd46..3286d4442097 100644
--- a/packages/react-devtools/preload.js
+++ b/packages/react-devtools/preload.js
@@ -36,6 +36,23 @@ contextBridge.exposeInMainWorld('api', {
     const host = process.env.HOST || 'localhost';
     const protocol = useHttps ? 'https' : 'http';
     const port = +process.env.REACT_DEVTOOLS_PORT || +process.env.PORT || 8097;
-    return {options, useHttps, host, protocol, port};
+    const path = process.env.REACT_DEVTOOLS_PATH || undefined;
+    const clientHost = process.env.REACT_DEVTOOLS_CLIENT_HOST || undefined;
+    const clientPort = process.env.REACT_DEVTOOLS_CLIENT_PORT
+      ? +process.env.REACT_DEVTOOLS_CLIENT_PORT
+      : undefined;
+    const clientUseHttps =
+      process.env.REACT_DEVTOOLS_CLIENT_USE_HTTPS === 'true' ? true : undefined;
+    return {
+      options,
+      useHttps,
+      host,
+      protocol,
+      port,
+      path,
+      clientHost,
+      clientPort,
+      clientUseHttps,
+    };
   },
 });

PATCH

echo "Patch applied successfully."
