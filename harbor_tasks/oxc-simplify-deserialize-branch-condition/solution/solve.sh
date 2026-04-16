#!/bin/bash
set -e

cd /workspace/oxc

# Check if already applied (idempotency check)
if grep -q "if (end <= firstNonAsciiPos)" napi/parser/src-js/generated/deserialize/js.js 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/apps/oxlint/src-js/generated/deserialize.js b/apps/oxlint/src-js/generated/deserialize.js
index 9af9befc7c5dd..3bec36aedf39d 100644
--- a/apps/oxlint/src-js/generated/deserialize.js
+++ b/apps/oxlint/src-js/generated/deserialize.js
@@ -8,7 +8,6 @@ let uint8,
   uint32,
   float64,
   sourceText,
-  sourceIsAscii,
   sourceStartPos,
   firstNonAsciiPos,
   parent = null,
@@ -42,14 +41,12 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = sourceStartPos, e = sourceStartPos + sourceByteLen; i < e; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i - sourceStartPos;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceStartPos + sourceByteLen;
+  else {
+    let i = sourceStartPos,
+      sourceEndPos = sourceStartPos + sourceByteLen;
+    for (; i < sourceEndPos && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   getLoc = getLocInput;
   return deserialize(uint32[536870900]);
@@ -5883,11 +5880,27 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos >= sourceStartPos && (sourceIsAscii || pos - sourceStartPos + len <= firstNonAsciiPos))
+  let end = pos + len;
+  // Note: Tried reducing this check to a single branch by making the comparison the equivalent of this Rust:
+  // `end.wrapping_sub(sourceStartPos) <= firstNonAsciiOffset`.
+  //
+  // The JS versions tried were:
+  // - `((end - sourceStartPos) >>> 0) <= firstNonAsciiOffset`
+  // - `((end - sourceStartPos) & 0x7FFF_FFFF) <= firstNonAsciiOffset`
+  // But it turned out that these are both slower by 5-10% on files which are all ASCII.
+  //
+  // `>>>` is slower as V8 can't assume result fits in an SMI (which is a 32-bit *signed* integer),
+  // as result could be greater or equal to `2 ** 31`. So it converts both the comparison's operands to `float64`s
+  // and does float compare (which is slower than integer compare).
+  //
+  // `& 0x7FFF_FFFF` is slower as it has a longer chain of data dependencies than the 2 independent
+  // branch comparisons.
+  //
+  // Both branches are very predictable, so 2 branches wins.
+  if (pos >= sourceStartPos && end <= firstNonAsciiPos)
     return sourceText.substr(pos - sourceStartPos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/js.js b/napi/parser/src-js/generated/deserialize/js.js
index 888e117e7c0a8..2f5fb891ef65e 100644
--- a/napi/parser/src-js/generated/deserialize/js.js
+++ b/napi/parser/src-js/generated/deserialize/js.js
@@ -1,14 +1,13 @@
 // Auto-generated code, DO NOT EDIT DIRECTLY!
 // To edit this generated file you have to edit `tasks/ast_tools/src/generators/raw_transfer.rs`.

-let uint8, uint32, float64, sourceText, sourceIsAscii, sourceEndPos, firstNonAsciiPos;
+let uint8, uint32, float64, sourceText, firstNonAsciiPos;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -19,14 +18,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -4546,11 +4542,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/js_parent.js b/napi/parser/src-js/generated/deserialize/js_parent.js
index c28ccf27855e0..dbaff1e3935bb 100644
--- a/napi/parser/src-js/generated/deserialize/js_parent.js
+++ b/napi/parser/src-js/generated/deserialize/js_parent.js
@@ -5,8 +5,6 @@ let uint8,
   uint32,
   float64,
   sourceText,
-  sourceIsAscii,
-  sourceEndPos,
   firstNonAsciiPos,
   parent = null;

@@ -15,7 +13,6 @@ const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -26,14 +23,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -5083,11 +5077,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/js_range.js b/napi/parser/src-js/generated/deserialize/js_range.js
index f290409d5a610..48ab1ca1f437f 100644
--- a/napi/parser/src-js/generated/deserialize/js_range.js
+++ b/napi/parser/src-js/generated/deserialize/js_range.js
@@ -1,14 +1,13 @@
 // Auto-generated code, DO NOT EDIT DIRECTLY!
 // To edit this generated file you have to edit `tasks/ast_tools/src/generators/raw_transfer.rs`.

-let uint8, uint32, float64, sourceText, sourceIsAscii, sourceEndPos, firstNonAsciiPos;
+let uint8, uint32, float64, sourceText, firstNonAsciiPos;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -19,14 +18,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -5088,11 +5084,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/js_range_parent.js b/napi/parser/src-js/generated/deserialize/js_range_parent.js
index 3924b38a0f6a3..3a5cede68a148 100644
--- a/napi/parser/src-js/generated/deserialize/js_range_parent.js
+++ b/napi/parser/src-js/generated/deserialize/js_range_parent.js
@@ -5,8 +5,6 @@ let uint8,
   uint32,
   float64,
   sourceText,
-  sourceIsAscii,
-  sourceEndPos,
   firstNonAsciiPos,
   parent = null;

@@ -15,7 +13,6 @@ const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -26,14 +23,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -5628,11 +5622,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/ts.js b/napi/parser/src-js/generated/deserialize/ts.js
index 4d85b35f2d15d..724cfed0a17f9 100644
--- a/napi/parser/src-js/generated/deserialize/ts.js
+++ b/napi/parser/src-js/generated/deserialize/ts.js
@@ -1,14 +1,13 @@
 // Auto-generated code, DO NOT EDIT DIRECTLY!
 // To edit this generated file you have to edit `tasks/ast_tools/src/generators/raw_transfer.rs`.

-let uint8, uint32, float64, sourceText, sourceIsAscii, sourceEndPos, firstNonAsciiPos;
+let uint8, uint32, float64, sourceText, firstNonAsciiPos;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -19,14 +18,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -4855,11 +4851,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/ts_parent.js b/napi/parser/src-js/generated/deserialize/ts_parent.js
index 3cf18084f1300..805610edf08f9 100644
--- a/napi/parser/src-js/generated/deserialize/ts_parent.js
+++ b/napi/parser/src-js/generated/deserialize/ts_parent.js
@@ -5,8 +5,6 @@ let uint8,
   uint32,
   float64,
   sourceText,
-  sourceIsAscii,
-  sourceEndPos,
   firstNonAsciiPos,
   parent = null;

@@ -15,7 +13,6 @@ const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -26,14 +23,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -5419,11 +5413,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/ts_range.js b/napi/parser/src-js/generated/deserialize/ts_range.js
index af91027f4698c..5257a4006d008 100644
--- a/napi/parser/src-js/generated/deserialize/ts_range.js
+++ b/napi/parser/src-js/generated/deserialize/ts_range.js
@@ -1,14 +1,13 @@
 // Auto-generated code, DO NOT EDIT DIRECTLY!
 // To edit this generated file you have to edit `tasks/ast_tools/src/generators/raw_transfer.rs`.

-let uint8, uint32, float64, sourceText, sourceIsAscii, sourceEndPos, firstNonAsciiPos;
+let uint8, uint32, float64, sourceText, firstNonAsciiPos;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -19,14 +18,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -5428,11 +5424,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/napi/parser/src-js/generated/deserialize/ts_range_parent.js b/napi/parser/src-js/generated/deserialize/ts_range_parent.js
index c89096e2d6168..1bbd7d895fccd 100644
--- a/napi/parser/src-js/generated/deserialize/ts_range_parent.js
+++ b/napi/parser/src-js/generated/deserialize/ts_range_parent.js
@@ -5,8 +5,6 @@ let uint8,
   uint32,
   float64,
   sourceText,
-  sourceIsAscii,
-  sourceEndPos,
   firstNonAsciiPos,
   parent = null;

@@ -15,7 +13,6 @@ const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   { fromCharCode } = String;

 export function deserialize(buffer, sourceText, sourceByteLen) {
-  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -26,14 +23,11 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  sourceIsAscii = sourceText.length === sourceByteLen;
-  if (!sourceIsAscii) {
-    firstNonAsciiPos = sourceByteLen;
-    for (let i = 0; i < sourceByteLen; i++)
-      if (uint8[i] >= 128) {
-        firstNonAsciiPos = i;
-        break;
-      }
+  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
+  else {
+    let i = 0;
+    for (; i < sourceByteLen && uint8[i] < 128; i++);
+    firstNonAsciiPos = i;
   }
   return deserialize(uint32[536870900]);
 }
@@ -5992,11 +5986,10 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-    return sourceText.substr(pos, len);
+  let end = pos + len;
+  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
   // Use `TextDecoder` for strings longer than 9 bytes.
   // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  let end = pos + len;
   if (len > 9) return decodeStr(uint8.subarray(pos, end));
   // Shorter strings decode by hand to avoid native call
   let out = "",
diff --git a/tasks/ast_tools/src/generators/raw_transfer.rs b/tasks/ast_tools/src/generators/raw_transfer.rs
index 389e224530479..19a00cdcbed1f 100644
--- a/tasks/ast_tools/src/generators/raw_transfer.rs
+++ b/tasks/ast_tools/src/generators/raw_transfer.rs
@@ -143,7 +143,7 @@ fn generate_deserializers(
         import {{ comments, initComments }} from '../plugins/comments.js';
         /* END_IF */

-        let uint8, uint32, float64, sourceText, sourceIsAscii, sourceStartPos, sourceEndPos, firstNonAsciiPos;
+        let uint8, uint32, float64, sourceText, sourceStartPos, firstNonAsciiPos;

         let parent = null;
         let getLoc;
@@ -166,7 +166,6 @@ fn generate_deserializers(

         /* IF !LINTER */
         export function deserialize(buffer, sourceText, sourceByteLen) {{
-            sourceEndPos = sourceByteLen;
             const data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
             resetBuffer();
             return data;
@@ -186,22 +185,28 @@ fn generate_deserializers(
             float64 = buffer.float64;

             sourceText = sourceTextInput;
-            sourceIsAscii = sourceText.length === sourceByteLen;

-            if (!sourceIsAscii) {{
-                // Find first non-ASCII byte in source region.
-                // `sourceText.substr()` can be used for strings ending before this position,
-                // since byte offsets equal char offsets in the all-ASCII prefix.
-                if (LINTER) {{
-                    firstNonAsciiPos = sourceByteLen;
-                    for (let i = sourceStartPos, e = sourceStartPos + sourceByteLen; i < e; i++) {{
-                        if (uint8[i] >= 128) {{ firstNonAsciiPos = i - sourceStartPos; break; }}
-                    }}
+            const sourceIsAscii = sourceText.length === sourceByteLen;
+
+            // Find first non-ASCII byte in source region.
+            // `sourceText.substr()` can be used for strings which are within source text and ending before
+            // this position, since byte offsets equal char offsets in the all-ASCII prefix.
+            if (LINTER) {{
+                if (sourceIsAscii === true) {{
+                    firstNonAsciiPos = sourceStartPos + sourceByteLen;
                 }} else {{
+                    let i = sourceStartPos;
+                    const sourceEndPos = sourceStartPos + sourceByteLen;
+                    for (; i < sourceEndPos && uint8[i] < 128; i++);
+                    firstNonAsciiPos = i;
+                }}
+            }} else {{
+                if (sourceIsAscii === true) {{
                     firstNonAsciiPos = sourceByteLen;
-                    for (let i = 0; i < sourceByteLen; i++) {{
-                        if (uint8[i] >= 128) {{ firstNonAsciiPos = i; break; }}
-                    }}
+                }} else {{
+                    let i = 0;
+                    for (; i < sourceByteLen && uint8[i] < 128; i++);
+                    firstNonAsciiPos = i;
                 }}
             }}

@@ -929,17 +934,34 @@ static STR_DESERIALIZER_BODY: &str = "

     pos = uint32[pos32];

+    const end = pos + len;
+
     if (LINTER) {
-        if (pos >= sourceStartPos && (sourceIsAscii || pos - sourceStartPos + len <= firstNonAsciiPos))
+        // Note: Tried reducing this check to a single branch by making the comparison the equivalent of this Rust:
+        // `end.wrapping_sub(sourceStartPos) <= firstNonAsciiOffset`.
+        //
+        // The JS versions tried were:
+        // - `((end - sourceStartPos) >>> 0) <= firstNonAsciiOffset`
+        // - `((end - sourceStartPos) & 0x7FFF_FFFF) <= firstNonAsciiOffset`
+        // But it turned out that these are both slower by 5-10% on files which are all ASCII.
+        //
+        // `>>>` is slower as V8 can't assume result fits in an SMI (which is a 32-bit *signed* integer),
+        // as result could be greater or equal to `2 ** 31`. So it converts both the comparison's operands to `float64`s
+        // and does float compare (which is slower than integer compare).
+        //
+        // `& 0x7FFF_FFFF` is slower as it has a longer chain of data dependencies than the 2 independent
+        // branch comparisons.
+        //
+        // Both branches are very predictable, so 2 branches wins.
+        if (pos >= sourceStartPos && end <= firstNonAsciiPos) {
             return sourceText.substr(pos - sourceStartPos, len);
+        }
     } else {
-        if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
-            return sourceText.substr(pos, len);
+        if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
     }

     // Use `TextDecoder` for strings longer than 9 bytes.
     // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-    const end = pos + len;
     if (len > 9) return decodeStr(uint8.subarray(pos, end));

     // Shorter strings decode by hand to avoid native call
PATCH

echo "Patch applied successfully!"
