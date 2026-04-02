#!/bin/bash
set -euo pipefail

# Check if patch is already applied (idempotency check)
if grep -q "cause?: JSONValue" packages/shared/ReactTypes.js 2>/dev/null; then
    echo "Patch already applied - Error.cause support exists"
    exit 0
fi

echo "Applying Error.cause support patch..."

git apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index fbf5190..098a1a6 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -8,6 +8,7 @@
  */

 import type {
+  JSONValue,
   Thenable,
   ReactDebugInfo,
   ReactDebugInfoEntry,
@@ -132,14 +133,6 @@ interface FlightStreamController {

 type UninitializedModel = string;

-export type JSONValue =
-  | number
-  | null
-  | boolean
-  | string
-  | {+[key: string]: JSONValue}
-  | $ReadOnlyArray<JSONValue>;
-
 type ProfilingResult = {
   track: number,
   endTime: number,
@@ -3527,6 +3520,18 @@ function resolveErrorDev(
   }

   let error;
+  const errorOptions =
+    'cause' in errorInfo
+      ? {
+          cause: reviveModel(
+            response,
+            // $FlowFixMe[incompatible-cast] -- Flow thinks `cause` in `cause?: JSONValue` can be undefined after `in` check.
+            (errorInfo.cause: JSONValue),
+            errorInfo,
+            'cause',
+          ),
+        }
+      : undefined;
   const callStack = buildFakeCallStack(
     response,
     stack,
@@ -3537,6 +3542,7 @@ function resolveErrorDev(
       null,
       message ||
         'An error occurred in the Server Components render but no message was provided',
+      errorOptions,
     ),
   );

diff --git a/packages/react-server/src/ReactFlightServer.js b/packages/react-server/src/ReactFlightServer.js
index 3bafdcf..4c50f6a 100644
--- a/packages/react-server/src/ReactFlightServer.js
+++ b/packages/react-server/src/ReactFlightServer.js
@@ -467,14 +467,6 @@ function getCurrentStackInDEV(): string {

 const ObjectPrototype = Object.prototype;

-type JSONValue =
-  | string
-  | boolean
-  | number
-  | null
-  | {+[key: string]: JSONValue}
-  | $ReadOnlyArray<JSONValue>;
-
 const stringify = JSON.stringify;

 type ReactJSONValue =
@@ -498,6 +490,7 @@ export type ReactClientValue =
   | React$Element<string>
   | React$Element<ClientReference<any> & any>
   | ReactComponentInfo
+  | ReactErrorInfo
   | string
   | boolean
   | number
@@ -4171,6 +4164,11 @@ function serializeErrorValue(request: Request, error: Error): string {
       stack = [];
     }
     const errorInfo: ReactErrorInfoDev = {name, message, stack, env};
+    if ('cause' in error) {
+      const cause: ReactClientValue = (error.cause: any);
+      const causeId = outlineModel(request, cause);
+      errorInfo.cause = serializeByValueID(causeId);
+    }
     const id = outlineModel(request, errorInfo);
     return '$Z' + id.toString(16);
   } else {
@@ -4181,7 +4179,11 @@ function serializeErrorValue(request: Request, error: Error): string {
   }
 }

-function serializeDebugErrorValue(request: Request, error: Error): string {
+function serializeDebugErrorValue(
+  request: Request,
+  counter: {objectLimit: number},
+  error: Error,
+): string {
   if (__DEV__) {
     let name: string = 'Error';
     let message: string;
@@ -4203,6 +4205,12 @@ function serializeDebugErrorValue(request: Request, error: Error): string {
       stack = [];
     }
     const errorInfo: ReactErrorInfoDev = {name, message, stack, env};
+    if ('cause' in error) {
+      counter.objectLimit--;
+      const cause: ReactClientValue = (error.cause: any);
+      const causeId = outlineDebugModel(request, counter, cause);
+      errorInfo.cause = serializeByValueID(causeId);
+    }
     const id = outlineDebugModel(
       request,
       {objectLimit: stack.length * 2 + 1},
@@ -4231,6 +4239,7 @@ function emitErrorChunk(
     let message: string;
     let stack: ReactStackTrace;
     let env = (0, request.environmentName)();
+    let causeReference: null | string = null;
     try {
       if (error instanceof Error) {
         name = error.name;
@@ -4243,6 +4252,13 @@ function emitErrorChunk(
           // Keep the environment name.
           env = errorEnv;
         }
+        if ('cause' in error) {
+          const cause: ReactClientValue = (error.cause: any);
+          const causeId = debug
+            ? outlineDebugModel(request, {objectLimit: 5}, cause)
+            : outlineModel(request, cause);
+          causeReference = serializeByValueID(causeId);
+        }
       } else if (typeof error === 'object' && error !== null) {
         message = describeObjectForErrorMessage(error);
         stack = [];
@@ -4258,6 +4274,9 @@ function emitErrorChunk(
     const ownerRef =
       owner == null ? null : outlineComponentInfo(request, owner);
     errorInfo = {digest, name, message, stack, env, owner: ownerRef};
+    if (causeReference !== null) {
+      (errorInfo: ReactErrorInfoDev).cause = causeReference;
+    }
   } else {
     errorInfo = {digest};
   }
@@ -4969,7 +4988,7 @@ function renderDebugModel(
       return serializeDebugFormData(request, value);
     }
     if (value instanceof Error) {
-      return serializeDebugErrorValue(request, value);
+      return serializeDebugErrorValue(request, counter, value);
     }
     if (value instanceof ArrayBuffer) {
       return serializeDebugTypedArray(request, 'A', new Uint8Array(value));
diff --git a/packages/shared/ReactTypes.js b/packages/shared/ReactTypes.js
index e58c36f..c865827 100644
--- a/packages/shared/ReactTypes.js
+++ b/packages/shared/ReactTypes.js
@@ -228,6 +228,14 @@ export type ReactErrorInfoProd = {
   +digest: string,
 };

+export type JSONValue =
+  | string
+  | boolean
+  | number
+  | null
+  | {+[key: string]: JSONValue}
+  | $ReadOnlyArray<JSONValue>;
+
 export type ReactErrorInfoDev = {
   +digest?: string,
   +name: string,
@@ -235,6 +243,7 @@ export type ReactErrorInfoDev = {
   +stack: ReactStackTrace,
   +env: string,
   +owner?: null | string,
+  cause?: JSONValue,
 };

 export type ReactErrorInfo = ReactErrorInfoProd | ReactErrorInfoDev;
PATCH

echo "Patch applied successfully!"
