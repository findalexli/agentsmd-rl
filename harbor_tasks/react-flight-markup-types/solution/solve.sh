set -euo pipefail

cd /workspace/react

# Check if already applied - look for the fixed type (non-opaque)
if ! grep -q "^export type ServerReferenceId = string;" packages/react-client/src/forks/ReactFlightClientConfig.markup.js; then
    echo "Applying fix..."

    # Apply the patch for markup config (remove opaque, fix parameter type)
    git apply - <<'PATCH'
diff --git a/packages/react-client/src/forks/ReactFlightClientConfig.markup.js b/packages/react-client/src/forks/ReactFlightClientConfig.markup.js
index 76a973b377b1..52f96ef9cbdf 100644
--- a/packages/react-client/src/forks/ReactFlightClientConfig.markup.js
+++ b/packages/react-client/src/forks/ReactFlightClientConfig.markup.js
@@ -18,7 +18,7 @@ export * from 'react-client/src/ReactClientConsoleConfigPlain';
 export type ModuleLoading = null;
 export type ServerConsumerModuleMap = null;
 export opaque type ServerManifest = null;
-export opaque type ServerReferenceId = string;
+export type ServerReferenceId = string;
 export opaque type ClientReferenceMetadata = null;
 export opaque type ClientReference<T> = null; // eslint-disable-line no-unused-vars

@@ -43,7 +43,7 @@ export function resolveClientReference<T>(

 export function resolveServerReference<T>(
   config: ServerManifest,
-  id: mixed,
+  id: ServerReferenceId,
 ): ClientReference<T> {
   throw new Error(
     'renderToHTML should not have emitted Server References. This is a bug in React.',
PATCH

    # Apply the patch for action server (use ServerReferenceId type in metadata)
    git apply - <<'PATCH'
diff --git a/packages/react-server/src/ReactFlightActionServer.js b/packages/react-server/src/ReactFlightActionServer.js
index ddcf36e96f99..5a47e9f9793 100644
--- a/packages/react-server/src/ReactFlightActionServer.js
+++ b/packages/react-server/src/ReactFlightActionServer.js
@@ -46,7 +46,7 @@ function bindArgs(fn: any, args: any) {
 function loadServerReference<T>(
   bundlerConfig: ServerManifest,
   metaData: {
-    id: string,
+    id: ServerReferenceId,
     bound: null | Promise<Array<any>>,
   },
 ): Promise<T> {
PATCH

    echo "Fix applied successfully."
else
    echo "Fix already applied."
fi
