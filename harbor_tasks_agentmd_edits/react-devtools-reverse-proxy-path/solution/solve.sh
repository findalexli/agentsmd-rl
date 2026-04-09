#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'prefixedPath' packages/react-devtools-core/src/backend.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/react-devtools-core/README.md b/packages/react-devtools-core/README.md
index a42e56969..3cced5e0e 100644
--- a/packages/react-devtools-core/README.md
+++ b/packages/react-devtools-core/README.md
@@ -54,6 +54,7 @@ Each filter object must include `type` and `isEnabled`. Some filters also requir
 |------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------|
 | `host`                 | `"localhost"` | Socket connection to frontend should use this host.                                                                       |
 | `isAppActive`          |               | (Optional) function that returns true/false, telling DevTools when it's ready to connect to React.                        |
+| `path`                 | `""`          | Path appended to the WebSocket URI (e.g. `"/__react_devtools__/"`). Useful when proxying through a reverse proxy on a subpath. A leading `/` is added automatically if missing. |
 | `port`                 | `8097`        | Socket connection to frontend should use this port.                                                                       |
 | `resolveRNStyle`       |               | (Optional) function that accepts a key (number) and returns a style (object); used by React Native.                       |
 | `retryConnectionDelay` | `200`         | Delay (ms) to wait between retrying a failed Websocket connection                                                         |
@@ -141,16 +142,51 @@ function onStatus(
 }
 ```

-#### `startServer(port?: number, host?: string, httpsOptions?: Object, loggerOptions?: Object)`
+#### `startServer(port?, host?, httpsOptions?, loggerOptions?, path?, clientOptions?)`
 Start a socket server (used to communicate between backend and frontend) and renders the DevTools UI.

 This method accepts the following parameters:
 | Name | Default | Description |
 |---|---|---|
-| `port` | `8097` | Socket connection to backend should use this port. |
-| `host` | `"localhost"` | Socket connection to backend should use this host. |
+| `port` | `8097` | Port the local server listens on. |
+| `host` | `"localhost"` | Host the local server binds to. |
 | `httpsOptions` | | _Optional_ object defining `key` and `cert` strings. |
 | `loggerOptions` | | _Optional_ object defining a `surface` string (to be included with DevTools logging events). |
+| `path` | | _Optional_ path to append to the WebSocket URI served to connecting clients (e.g. `"/__react_devtools__/"`). Also set via the `REACT_DEVTOOLS_PATH` env var in the Electron app. |
+| `clientOptions` | | _Optional_ object with client-facing overrides (see below). |
+
+##### `clientOptions`
+
+When connecting through a reverse proxy, the client may need to connect to a different host, port, or protocol than the local server. Use `clientOptions` to override what appears in the `connectToDevTools()` script served to clients. Any field not set falls back to the corresponding server value.
+
+| Field | Default | Description |
+|---|---|---|
+| `host` | server `host` | Host the client connects to. |
+| `port` | server `port` | Port the client connects to. |
+| `useHttps` | server `useHttps` | Whether the client should use `wss://`. |
+
+These can also be set via environment variables in the Electron app:
+
+| Env Var | Description |
+|---|---|
+| `REACT_DEVTOOLS_CLIENT_HOST` | Overrides the host in the served client script. |
+| `REACT_DEVTOOLS_CLIENT_PORT` | Overrides the port in the served client script. |
+| `REACT_DEVTOOLS_CLIENT_USE_HTTPS` | Set to `"true"` to make the served client script use `wss://`. |
+
+##### Reverse proxy example
+
+Run DevTools locally on the default port, but tell clients to connect through a remote proxy:
+```sh
+REACT_DEVTOOLS_CLIENT_HOST=remote.example.com \
+REACT_DEVTOOLS_CLIENT_PORT=443 \
+REACT_DEVTOOLS_CLIENT_USE_HTTPS=true \
+REACT_DEVTOOLS_PATH=/__react_devtools__/ \
+react-devtools
+```
+The server listens on `localhost:8097`. The served script tells clients:
+```js
+connectToDevTools({host: 'remote.example.com', port: 443, useHttps: true, path: '/__react_devtools__/'})
+```

 # Development

diff --git a/packages/react-devtools-core/src/backend.js b/packages/react-devtools-core/src/backend.js
index 262b3bc04..075758f78 100644
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
index ccf4fd60b..81f357751 100644
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
@@ -358,15 +377,21 @@ function startServer(
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
         `var ReactDevToolsBackend = typeof ReactDevToolsBackend !== "undefined" ? ReactDevToolsBackend : require("ReactDevToolsBackend");\n` +
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
@@ -374,7 +399,18 @@ function startServer(
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
diff --git a/packages/react-devtools/README.md b/packages/react-devtools/README.md
index 8c436c1fb..faa71dcc5 100644
--- a/packages/react-devtools/README.md
+++ b/packages/react-devtools/README.md
@@ -87,7 +87,31 @@ This will ensure the developer tools are connected. **Don't forget to remove i

 ## Advanced

-By default DevTools listen to port `8097` on `localhost`. The port can be modified by setting the `REACT_DEVTOOLS_PORT` environment variable. If you need to further customize host, port, or other settings, see the `react-devtools-core` package instead.
+By default DevTools listen to port `8097` on `localhost`. If you need to customize the server or client connection settings, the following environment variables are available:
+
+| Env Var | Default | Description |
+|---|---|---|
+| `HOST` | `"localhost"` | Host the local server binds to. |
+| `PORT` | `8097` | Port the local server listens on. |
+| `REACT_DEVTOOLS_PORT` | | Alias for `PORT`. Takes precedence if both are set. |
+| `KEY` | | Path to an SSL key file. Enables HTTPS when set alongside `CERT`. |
+| `CERT` | | Path to an SSL certificate file. Enables HTTPS when set alongside `KEY`. |
+| `REACT_DEVTOOLS_PATH` | | Path appended to the WebSocket URI served to clients (e.g. `/__react_devtools__/`). |
+| `REACT_DEVTOOLS_CLIENT_HOST` | `HOST` | Overrides the host in the script served to connecting clients. |
+| `REACT_DEVTOOLS_CLIENT_PORT` | `PORT` | Overrides the port in the script served to connecting clients. |
+| `REACT_DEVTOOLS_CLIENT_USE_HTTPS` | | Set to `"true"` to make the served client script use `wss://`. |
+
+When connecting through a reverse proxy, use the `REACT_DEVTOOLS_CLIENT_*` variables to tell clients to connect to a different host/port/protocol than the local server:
+
+```sh
+REACT_DEVTOOLS_CLIENT_HOST=remote.example.com \
+REACT_DEVTOOLS_CLIENT_PORT=443 \
+REACT_DEVTOOLS_CLIENT_USE_HTTPS=true \
+REACT_DEVTOOLS_PATH=/__react_devtools__/ \
+react-devtools
+```
+
+For more details, see the [`react-devtools-core` documentation](https://github.com/facebook/react/tree/main/packages/react-devtools-core).

 ## FAQ

diff --git a/packages/react-devtools/app.html b/packages/react-devtools/app.html
index 7b55e0d37..1d11394c9 100644
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
index 33a9e3d6d..3286d4442 100644
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
