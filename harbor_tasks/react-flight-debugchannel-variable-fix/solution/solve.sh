#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react-repo

# Check if already applied
echo "Checking if patch is already applied..."
if grep -q "debugChannelReadable !== undefined" packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js; then
    echo "Patch already applied, skipping."
    exit 0
fi

echo "Applying patch..."
git apply - <<'PATCH'
commit 2dd9b7cf76c31df5d7e26e5199e3c362c3e94f95
Author: React Team <react@example.com>
Date:   Fri Mar 7 00:00:00 2025 -0500

    [Flight] Fix debug channel flag in Node.js server renderToPipeableStream

diff --git a/packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js b/packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js
index 9c167223bacc..a4bda173f158 100644
--- a/packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js
+++ b/packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js
@@ -187,7 +187,7 @@ function renderToPipeableStream(
     options ? options.startTime : undefined,
     __DEV__ && options ? options.environmentName : undefined,
     __DEV__ && options ? options.filterStackFrame : undefined,
-    debugChannel !== undefined,
+    debugChannelReadable !== undefined,
   );
   let hasStartedFlowing = false;
   startWork(request);
diff --git a/packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js b/packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js
index 910561aca51a..d267edd085af 100644
--- a/packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js
+++ b/packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js
@@ -199,7 +199,7 @@ export function renderToPipeableStream(
     options ? options.startTime : undefined,
     __DEV__ && options ? options.environmentName : undefined,
     __DEV__ && options ? options.filterStackFrame : undefined,
-    debugChannel !== undefined,
+    debugChannelReadable !== undefined,
   );
   let hasStartedFlowing = false;
   startWork(request);
diff --git a/packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js b/packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js
index 1590aa6a37c9..5381072b3ad8 100644
--- a/packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js
+++ b/packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js
@@ -193,7 +193,7 @@ function renderToPipeableStream(
     options ? options.startTime : undefined,
     __DEV__ && options ? options.environmentName : undefined,
     __DEV__ && options ? options.filterStackFrame : undefined,
-    debugChannel !== undefined,
+    debugChannelReadable !== undefined,
   );
   let hasStartedFlowing = false;
   startWork(request);
PATCH

echo "Patch applied successfully!"
