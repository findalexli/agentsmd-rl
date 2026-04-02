#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied (look for reviveModel function in the patched file)
if grep -q "function reviveModel(" packages/react-client/src/ReactFlightClient.js; then
    echo "Patch already applied, skipping."
    exit 0
fi

echo "Applying React Flight Client optimization patch..."

git apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index 20aa8ce8f9a3..5512a75a5043 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -355,7 +355,6 @@ type Response = {
   _encodeFormAction: void | EncodeFormActionCallback,
   _nonce: ?string,
   _chunks: Map<number, SomeChunk<any>>,
-  _fromJSON: (key: string, value: JSONValue) => any,
   _stringDecoder: StringDecoder,
   _closed: boolean,
   _closedReason: mixed,
@@ -2286,6 +2285,11 @@ function defineLazyGetter<T>(
         // TODO: We should ideally throw here to indicate a difference.
         return OMITTED_PROP_ERROR;
       },
+      // no-op: the walk function may try to reassign this property after
+      // parseModelString returns. With the JSON.parse reviver, the engine's
+      // internal CreateDataProperty silently failed. We use a no-op setter
+      // to match that behavior in strict mode.
+      set: function () {},
       enumerable: true,
       configurable: false,
     });
@@ -2606,6 +2610,11 @@ function parseModelString(
                 // TODO: We should ideally throw here to indicate a difference.
                 return OMITTED_PROP_ERROR;
               },
+              // no-op: the walk function may try to reassign this property
+              // after parseModelString returns. With the JSON.parse reviver,
+              // the engine's internal CreateDataProperty silently failed.
+              // We use a no-op setter to match that behavior in strict mode.
+              set: function () {},
               enumerable: true,
               configurable: false,
             });
@@ -2683,7 +2692,6 @@ function ResponseInstance(
   this._nonce = nonce;
   this._chunks = chunks;
   this._stringDecoder = createStringDecoder();
-  this._fromJSON = (null: any);
   this._closed = false;
   this._closedReason = null;
   this._allowPartialStream = allowPartialStream;
@@ -2767,9 +2775,6 @@ function ResponseInstance(
       markAllTracksInOrder();
     }
   }
-
-  // Don't inline this call because it causes closure to outline the call above.
-  this._fromJSON = createFromJSONCallback(this);
 }

 export function createResponse(
@@ -5237,24 +5242,52 @@ export function processStringChunk(
 }

 function parseModel<T>(response: Response, json: UninitializedModel): T {
-  return JSON.parse(json, response._fromJSON);
+  const rawModel = JSON.parse(json);
+  // Pass a wrapper object as parentObject to match the original JSON.parse
+  // reviver behavior, where the root value's reviver receives {"": rootValue}
+  // as `this`. This ensures parentObject is never null when accessed downstream.
+  return reviveModel(response, rawModel, {'': rawModel}, '');
 }

-function createFromJSONCallback(response: Response) {
-  // $FlowFixMe[missing-this-annot]
-  return function (key: string, value: JSONValue) {
-    if (key === __PROTO__) {
-      return undefined;
+function reviveModel(
+  response: Response,
+  value: JSONValue,
+  parentObject: Object,
+  key: string,
+): any {
+  if (typeof value === 'string') {
+    if (value[0] === '$') {
+      return parseModelString(response, parentObject, key, value);
     }
-    if (typeof value === 'string') {
-      // We can't use .bind here because we need the "this" value.
-      return parseModelString(response, this, key, value);
+    return value;
+  }
+  if (typeof value !== 'object' || value === null) {
+    return value;
+  }
+  if (isArray(value)) {
+    for (let i = 0; i < value.length; i++) {
+      (value: any)[i] = reviveModel(response, value[i], value, '' + i);
     }
-    if (typeof value === 'object' && value !== null) {
+    if (value[0] === REACT_ELEMENT_TYPE) {
+      // React element tuple
       return parseModelTuple(response, value);
     }
     return value;
-  };
+  }
+  // Plain object
+  for (const k in value) {
+    if (k === __PROTO__) {
+      delete (value: any)[k];
    } else {
-      return value;
+      const walked = reviveModel(response, (value: any)[k], value, k);
+      if (walked !== undefined) {
+        (value: any)[k] = walked;
+      } else {
+        delete (value: any)[k];
+      }
     }
-  };
+  }
+  return value;
 }

 export function close(weakResponse: WeakResponse): void {
diff --git a/packages/react-noop-renderer/src/ReactNoopFlightClient.js b/packages/react-noop-renderer/src/ReactNoopFlightClient.js
index a5c43bd65259..4699b149e85f 100644
--- a/packages/react-noop-renderer/src/ReactNoopFlightClient.js
+++ b/packages/react-noop-renderer/src/ReactNoopFlightClient.js
@@ -43,9 +43,6 @@ const {createResponse, createStreamState, processBinaryChunk, getRoot, close} =
     requireModule(idx: string) {
       return readModule(idx);
     },
-    parseModel(response: Response, json) {
-      return JSON.parse(json, response._fromJSON);
-    },
     bindToConsole(methodName, args, badgeName) {
       return Function.prototype.bind.apply(
         // eslint-disable-next-line react-internal/no-production-logging
PATCH

echo "Patch applied successfully."
