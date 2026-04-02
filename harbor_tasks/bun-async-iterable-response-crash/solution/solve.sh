#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if already patched, exit
if grep -q '!= null' src/js/builtins/ReadableStream.ts 2>/dev/null && \
   grep -q 'var sink = this.\$sink;' src/js/builtins/ReadableStreamInternals.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/webcore/ReadableStream.cpp b/src/bun.js/bindings/webcore/ReadableStream.cpp
index ef0a2cd6a05..46c42988374 100644
--- a/src/bun.js/bindings/webcore/ReadableStream.cpp
+++ b/src/bun.js/bindings/webcore/ReadableStream.cpp
@@ -486,6 +486,7 @@ static inline JSC::EncodedJSValue ZigGlobalObject__readableStreamToArrayBufferBo

     auto callData = JSC::getCallData(function);
     JSValue result = call(globalObject, function, callData, JSC::jsUndefined(), arguments);
+    RETURN_IF_EXCEPTION(throwScope, {});

     JSC::JSObject* object = result.getObject();

@@ -493,14 +494,12 @@ static inline JSC::EncodedJSValue ZigGlobalObject__readableStreamToArrayBufferBo
         return JSValue::encode(result);

     if (!object) [[unlikely]] {
-        auto throwScope = DECLARE_THROW_SCOPE(vm);
         throwTypeError(globalObject, throwScope, "Expected object"_s);
         return {};
     }

     JSC::JSPromise* promise = JSC::jsDynamicCast<JSC::JSPromise*>(object);
     if (!promise) [[unlikely]] {
-        auto throwScope = DECLARE_THROW_SCOPE(vm);
         throwTypeError(globalObject, throwScope, "Expected promise"_s);
         return {};
     }
@@ -530,6 +529,7 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToBytes(Zig::Globa

     auto callData = JSC::getCallData(function);
     JSValue result = call(globalObject, function, callData, JSC::jsUndefined(), arguments);
+    RETURN_IF_EXCEPTION(throwScope, {});

     JSC::JSObject* object = result.getObject();

@@ -537,14 +537,12 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToBytes(Zig::Globa
         return JSValue::encode(result);

     if (!object) [[unlikely]] {
-        auto throwScope = DECLARE_THROW_SCOPE(vm);
         throwTypeError(globalObject, throwScope, "Expected object"_s);
         return {};
     }

     JSC::JSPromise* promise = JSC::jsDynamicCast<JSC::JSPromise*>(object);
     if (!promise) [[unlikely]] {
-        auto throwScope = DECLARE_THROW_SCOPE(vm);
         throwTypeError(globalObject, throwScope, "Expected promise"_s);
         return {};
     }
@@ -555,6 +553,7 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToBytes(Zig::Globa
 extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToText(Zig::GlobalObject* globalObject, JSC::EncodedJSValue readableStreamValue)
 {
     auto& vm = JSC::getVM(globalObject);
+    auto throwScope = DECLARE_THROW_SCOPE(vm);

     JSC::JSFunction* function = nullptr;
     if (auto readableStreamToText = globalObject->m_readableStreamToText.get()) {
@@ -569,12 +568,15 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToText(Zig::Global
     arguments.append(JSValue::decode(readableStreamValue));

     auto callData = JSC::getCallData(function);
-    return JSC::JSValue::encode(call(globalObject, function, callData, JSC::jsUndefined(), arguments));
+    JSValue result = call(globalObject, function, callData, JSC::jsUndefined(), arguments);
+    RETURN_IF_EXCEPTION(throwScope, {});
+    return JSC::JSValue::encode(result);
 }

 extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToFormData(Zig::GlobalObject* globalObject, JSC::EncodedJSValue readableStreamValue, JSC::EncodedJSValue contentTypeValue)
 {
     auto& vm = JSC::getVM(globalObject);
+    auto throwScope = DECLARE_THROW_SCOPE(vm);

     JSC::JSFunction* function = nullptr;
     if (auto readableStreamToFormData = globalObject->m_readableStreamToFormData.get()) {
@@ -590,12 +592,15 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToFormData(Zig::Gl
     arguments.append(JSValue::decode(contentTypeValue));

     auto callData = JSC::getCallData(function);
-    return JSC::JSValue::encode(call(globalObject, function, callData, JSC::jsUndefined(), arguments));
+    JSValue result = call(globalObject, function, callData, JSC::jsUndefined(), arguments);
+    RETURN_IF_EXCEPTION(throwScope, {});
+    return JSC::JSValue::encode(result);
 }

 extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToJSON(Zig::GlobalObject* globalObject, JSC::EncodedJSValue readableStreamValue)
 {
     auto& vm = JSC::getVM(globalObject);
+    auto throwScope = DECLARE_THROW_SCOPE(vm);

     JSC::JSFunction* function = nullptr;
     if (auto readableStreamToJSON = globalObject->m_readableStreamToJSON.get()) {
@@ -610,12 +615,15 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToJSON(Zig::Global
     arguments.append(JSValue::decode(readableStreamValue));

     auto callData = JSC::getCallData(function);
-    return JSC::JSValue::encode(call(globalObject, function, callData, JSC::jsUndefined(), arguments));
+    JSValue result = call(globalObject, function, callData, JSC::jsUndefined(), arguments);
+    RETURN_IF_EXCEPTION(throwScope, {});
+    return JSC::JSValue::encode(result);
 }

 extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToBlob(Zig::GlobalObject* globalObject, JSC::EncodedJSValue readableStreamValue)
 {
     auto& vm = JSC::getVM(globalObject);
+    auto throwScope = DECLARE_THROW_SCOPE(vm);

     JSC::JSFunction* function = nullptr;
     if (auto readableStreamToBlob = globalObject->m_readableStreamToBlob.get()) {
@@ -630,7 +638,9 @@ extern "C" JSC::EncodedJSValue ZigGlobalObject__readableStreamToBlob(Zig::Global
     arguments.append(JSValue::decode(readableStreamValue));

     auto callData = JSC::getCallData(function);
-    return JSC::JSValue::encode(call(globalObject, function, callData, JSC::jsUndefined(), arguments));
+    JSValue result = call(globalObject, function, callData, JSC::jsUndefined(), arguments);
+    RETURN_IF_EXCEPTION(throwScope, {});
+    return JSC::JSValue::encode(result);
 }

 JSC_DEFINE_HOST_FUNCTION(functionReadableStreamToArrayBuffer, (JSC::JSGlobalObject * globalObject, JSC::CallFrame* callFrame))
diff --git a/src/js/builtins/ReadableStream.ts b/src/js/builtins/ReadableStream.ts
index c4c17f5cab8..fc7d299eabf 100644
--- a/src/js/builtins/ReadableStream.ts
+++ b/src/js/builtins/ReadableStream.ts
@@ -111,7 +111,7 @@ export function readableStreamToArray(stream: ReadableStream): Promise<unknown[]
   if (!$isReadableStream(stream)) throw $ERR_INVALID_ARG_TYPE("stream", "ReadableStream", typeof stream);
   // this is a direct stream
   var underlyingSource = $getByIdDirectPrivate(stream, "underlyingSource");
-  if (underlyingSource !== undefined) {
+  if (underlyingSource != null) {
     return $readableStreamToArrayDirect(stream, underlyingSource);
   }
   if ($isReadableStreamLocked(stream)) return Promise.$reject($ERR_INVALID_STATE_TypeError("ReadableStream is locked"));
@@ -123,7 +123,7 @@ export function readableStreamToText(stream: ReadableStream): Promise<string> {
   if (!$isReadableStream(stream)) throw $ERR_INVALID_ARG_TYPE("stream", "ReadableStream", typeof stream);
   // this is a direct stream
   var underlyingSource = $getByIdDirectPrivate(stream, "underlyingSource");
-  if (underlyingSource !== undefined) {
+  if (underlyingSource != null) {
     return $readableStreamToTextDirect(stream, underlyingSource);
   }
   if ($isReadableStreamLocked(stream)) return Promise.$reject($ERR_INVALID_STATE_TypeError("ReadableStream is locked"));
@@ -142,7 +142,7 @@ export function readableStreamToArrayBuffer(stream: ReadableStream<ArrayBuffer>)
   if (!$isReadableStream(stream)) throw $ERR_INVALID_ARG_TYPE("stream", "ReadableStream", typeof stream);
   // this is a direct stream
   var underlyingSource = $getByIdDirectPrivate(stream, "underlyingSource");
-  if (underlyingSource !== undefined) {
+  if (underlyingSource != null) {
     return $readableStreamToArrayBufferDirect(stream, underlyingSource, false);
   }
   if ($isReadableStreamLocked(stream)) return Promise.$reject($ERR_INVALID_STATE_TypeError("ReadableStream is locked"));
@@ -223,7 +223,7 @@ export function readableStreamToBytes(stream: ReadableStream<ArrayBuffer>): Prom
   // this is a direct stream
   var underlyingSource = $getByIdDirectPrivate(stream, "underlyingSource");

-  if (underlyingSource !== undefined) {
+  if (underlyingSource != null) {
     return $readableStreamToArrayBufferDirect(stream, underlyingSource, true);
   }
   if ($isReadableStreamLocked(stream)) return Promise.$reject($ERR_INVALID_STATE_TypeError("ReadableStream is locked"));
diff --git a/src/js/builtins/ReadableStreamInternals.ts b/src/js/builtins/ReadableStreamInternals.ts
index cc37b617c7c..a2440f52d86 100644
--- a/src/js/builtins/ReadableStreamInternals.ts
+++ b/src/js/builtins/ReadableStreamInternals.ts
@@ -1148,6 +1148,9 @@ export function onCloseDirectStream(reason) {
     return;
   }

+  var sink = this.$sink;
+  if (!sink) return;
+
   $putByIdDirectPrivate(stream, "state", $streamClosing);
   if (typeof this.$underlyingSource.close === "function") {
     try {
@@ -1157,7 +1160,7 @@ export function onCloseDirectStream(reason) {

   var flushed;
   try {
-    flushed = this.$sink.end();
+    flushed = sink.end();
     $putByIdDirectPrivate(this, "sink", undefined);
   } catch (e) {
     if (this._pendingRead) {
@@ -1220,6 +1223,8 @@ export function onCloseDirectStream(reason) {
 export function onFlushDirectStream() {
   var stream = this.$controlledReadableStream;
   if (!stream) return;
+  var sink = this.$sink;
+  if (!sink) return;
   var reader = $getByIdDirectPrivate(stream, "reader");
   if (!reader || !$isReadableStreamDefaultReader(reader)) {
     return;
@@ -1228,7 +1233,7 @@ export function onFlushDirectStream() {
   var _pendingRead = this._pendingRead;
   this._pendingRead = undefined;
   if (_pendingRead && $isPromise(_pendingRead)) {
-    var flushed = this.$sink.flush();
+    var flushed = sink.flush();
     if (flushed?.byteLength) {
       this._pendingRead = $getByIdDirectPrivate(stream, "readRequests")?.shift();
       $fulfillPromise(_pendingRead, { value: flushed, done: false });
@@ -1236,7 +1241,7 @@ export function onFlushDirectStream() {
       this._pendingRead = _pendingRead;
     }
   } else if ($getByIdDirectPrivate(stream, "readRequests")?.isNotEmpty()) {
-    var flushed = this.$sink.flush();
+    var flushed = sink.flush();
     if (flushed?.byteLength) {
       $readableStreamFulfillReadRequest(stream, flushed, false);
     }
@@ -2259,6 +2264,9 @@ export function readableStreamToArrayBufferDirect(
 ) {
   var sink = new Bun.ArrayBufferSink();
   $putByIdDirectPrivate(stream, "underlyingSource", null);
+  $putByIdDirectPrivate(stream, "start", undefined);
+  $putByIdDirectPrivate(stream, "reader", {});
+  stream.$disturbed = true;
   var highWaterMark = $getByIdDirectPrivate(stream, "highWaterMark");
   sink.start({ highWaterMark, asUint8Array });
   var capability = $newPromiseCapability(Promise);
@@ -2298,11 +2306,15 @@ export function readableStreamToArrayBufferDirect(
     var firstPull = pull(controller);
   } catch (e) {
     didError = true;
+    $putByIdDirectPrivate(stream, "reader", undefined);
     $readableStreamError(stream, e);
     return Promise.$reject(e);
   } finally {
-    if (!$isPromise(firstPull)) {
-      if (!didError && stream) $readableStreamCloseIfPossible(stream);
+    if (!$isPromise(firstPull) && !didError) {
+      if (stream) {
+        $putByIdDirectPrivate(stream, "reader", undefined);
+        $readableStreamCloseIfPossible(stream);
+      }
       controller = close = sink = pull = stream = undefined;
       return capability.promise;
     }
@@ -2311,12 +2323,16 @@ export function readableStreamToArrayBufferDirect(
   $assert($isPromise(firstPull));
   return firstPull.then(
     () => {
-      if (!didError && stream) $readableStreamCloseIfPossible(stream);
+      if (!didError && stream) {
+        $putByIdDirectPrivate(stream, "reader", undefined);
+        $readableStreamCloseIfPossible(stream);
+      }
       controller = close = sink = pull = stream = undefined;
       return capability.promise;
     },
     e => {
       didError = true;
+      $putByIdDirectPrivate(stream, "reader", undefined);
       if ($getByIdDirectPrivate(stream, "state") === $streamReadable) $readableStreamError(stream, e);
       return Promise.$reject(e);
     },

PATCH
