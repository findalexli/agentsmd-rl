#!/bin/bash
set -e

cd /workspace/oxc

# Check if already patched
if grep -q "const { latin1Slice } = Buffer.prototype," napi/parser/src-js/generated/deserialize/js.js 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/apps/oxlint/src-js/generated/deserialize.js b/apps/oxlint/src-js/generated/deserialize.js
index 716ce0875af5d..d7def457b7059 100644
--- a/apps/oxlint/src-js/generated/deserialize.js
+++ b/apps/oxlint/src-js/generated/deserialize.js
@@ -8,6 +8,7 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
   sourceStartPos = 0,
   firstNonAsciiPos = 0,
   parent = null,
@@ -16,14 +17,18 @@ let uint8,
 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
   { fromCharCode } = String,
-  NodeProto = Object.create(Object.prototype, {
-    loc: {
-      get() {
-        return getLoc(this);
-      },
-      enumerable: true,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);
+
+const NodeProto = Object.create(Object.prototype, {
+  loc: {
+    get() {
+      return getLoc(this);
     },
-  });
+    enumerable: true,
+  },
+});

 export function deserializeProgramOnly(
   buffer,
@@ -41,20 +46,23 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceStartPos + sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceStartPos + sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = sourceStartPos,
       sourceEndPos = sourceStartPos + sourceByteLen;
     for (; i < sourceEndPos && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, sourceStartPos, sourceEndPos);
   }
   getLoc = getLocInput;
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5880,40 +5888,30 @@ function deserializeStr(pos) {
     len = uint32[pos32 + 2];
   if (len === 0) return "";
   pos = uint32[pos32];
-  let end = pos + len;
-  // Note: Tried reducing this check to a single branch by making the comparison the equivalent of this Rust:
-  // `end.wrapping_sub(sourceStartPos) <= firstNonAsciiOffset`.
-  //
-  // The JS versions tried were:
-  // - `((end - sourceStartPos) >>> 0) <= firstNonAsciiOffset`
-  // - `((end - sourceStartPos) & 0x7FFF_FFFF) <= firstNonAsciiOffset`
-  // But it turned out that these are both slower by 5-10% on files which are all ASCII.
-  //
-  // `>>>` is slower as V8 can't assume result fits in an SMI (which is a 32-bit *signed* integer),
-  // as result could be greater or equal to `2 ** 31`. So it converts both the comparison's operands to `float64`s
-  // and does float compare (which is slower than integer compare).
-  //
-  // `& 0x7FFF_FFFF` is slower as it has a longer chain of data dependencies than the 2 independent
-  // branch comparisons.
-  //
-  // Both branches are very predictable, so 2 branches wins.
-  if (pos >= sourceStartPos && end <= firstNonAsciiPos)
-    return sourceText.substr(pos - sourceStartPos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  let end = pos + len,
+    isInSourceRegion = pos >= sourceStartPos;
+  if (isInSourceRegion && end <= firstNonAsciiPos)
+    return sourceTextLatin.substr(pos - sourceStartPos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  // If string is in source region, use slice of `sourceTextLatin` if all ASCII
+  if (isInSourceRegion) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos - sourceStartPos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecDirective(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/js.js b/napi/parser/src-js/generated/deserialize/js.js
index bfad0fa40a8b8..fe652b4b4cdf7 100644
--- a/napi/parser/src-js/generated/deserialize/js.js
+++ b/napi/parser/src-js/generated/deserialize/js.js
@@ -5,13 +5,19 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -22,18 +28,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -4547,22 +4556,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/js_parent.js b/napi/parser/src-js/generated/deserialize/js_parent.js
index 71f5298cf556b..7f9298492f290 100644
--- a/napi/parser/src-js/generated/deserialize/js_parent.js
+++ b/napi/parser/src-js/generated/deserialize/js_parent.js
@@ -5,14 +5,20 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0,
   parent = null;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -23,18 +29,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5078,22 +5087,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/js_range.js b/napi/parser/src-js/generated/deserialize/js_range.js
index 5c2cf2be3bf29..fe74dc7d4bcd3 100644
--- a/napi/parser/src-js/generated/deserialize/js_range.js
+++ b/napi/parser/src-js/generated/deserialize/js_range.js
@@ -5,13 +5,19 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -22,18 +28,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5089,22 +5098,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/js_range_parent.js b/napi/parser/src-js/generated/deserialize/js_range_parent.js
index 379ef21801b77..932221b0a50ef 100644
--- a/napi/parser/src-js/generated/deserialize/js_range_parent.js
+++ b/napi/parser/src-js/generated/deserialize/js_range_parent.js
@@ -5,14 +5,20 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0,
   parent = null;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -23,18 +29,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5623,22 +5632,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/ts.js b/napi/parser/src-js/generated/deserialize/ts.js
index b5bf97cd804b2..2616fb217a603 100644
--- a/napi/parser/src-js/generated/deserialize/ts.js
+++ b/napi/parser/src-js/generated/deserialize/ts.js
@@ -5,13 +5,19 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -22,18 +28,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -4856,22 +4865,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/ts_parent.js b/napi/parser/src-js/generated/deserialize/ts_parent.js
index 2b495eaf435f5..f8583be6b64bf 100644
--- a/napi/parser/src-js/generated/deserialize/ts_parent.js
+++ b/napi/parser/src-js/generated/deserialize/ts_parent.js
@@ -5,14 +5,20 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0,
   parent = null;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -23,18 +29,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5414,22 +5423,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/ts_range.js b/napi/parser/src-js/generated/deserialize/ts_range.js
index 588f379a3f071..c40d72dabb786 100644
--- a/napi/parser/src-js/generated/deserialize/ts_range.js
+++ b/napi/parser/src-js/generated/deserialize/ts_range.js
@@ -5,13 +5,19 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -22,18 +28,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5429,22 +5438,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/napi/parser/src-js/generated/deserialize/ts_range_parent.js b/napi/parser/src-js/generated/deserialize/ts_range_parent.js
index 4f6e2a7d0eaee..33da28813e615 100644
--- a/napi/parser/src-js/generated/deserialize/ts_range_parent.js
+++ b/napi/parser/src-js/generated/deserialize/ts_range_parent.js
@@ -5,14 +5,20 @@ let uint8,
   uint32,
   float64,
   sourceText,
+  sourceTextLatin,
+  sourceEndPos = 0,
   firstNonAsciiPos = 0,
   parent = null;

 const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),
   decodeStr = textDecoder.decode.bind(textDecoder),
-  { fromCharCode } = String;
+  { fromCharCode } = String,
+  { latin1Slice } = Buffer.prototype,
+  stringDecodeArrays = Array(65).fill(null);
+for (let i = 0; i <= 64; i++) stringDecodeArrays[i] = Array(i).fill(0);

 export function deserialize(buffer, sourceText, sourceByteLen) {
+  sourceEndPos = sourceByteLen;
   let data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
   resetBuffer();
   return data;
@@ -23,18 +29,21 @@ function deserializeWith(buffer, sourceTextInput, sourceByteLen, getLocInput, de
   uint32 = buffer.uint32;
   float64 = buffer.float64;
   sourceText = sourceTextInput;
-  if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
-  else {
+  if (sourceText.length === sourceByteLen) {
+    firstNonAsciiPos = sourceByteLen;
+    sourceTextLatin = sourceText;
+  } else {
     let i = 0;
     for (; i < sourceByteLen && uint8[i] < 128; i++);
     firstNonAsciiPos = i;
+    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
   }
   return deserialize(uint32[536870900]);
 }

 export function resetBuffer() {
-  // Clear buffer and source text string to allow them to be garbage collected
-  uint8 = uint32 = float64 = sourceText = void 0;
+  // Clear buffer and source text strings to allow them to be garbage collected
+  uint8 = uint32 = float64 = sourceText = sourceTextLatin = void 0;
 }

 function deserializeProgram(pos) {
@@ -5987,22 +5996,26 @@ function deserializeStr(pos) {
   if (len === 0) return "";
   pos = uint32[pos32];
   let end = pos + len;
-  if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
-  // Use `TextDecoder` for strings longer than 9 bytes.
-  // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-  if (len > 9) return decodeStr(uint8.subarray(pos, end));
-  // Shorter strings decode by hand to avoid native call
-  let out = "",
-    c;
-  do {
-    c = uint8[pos++];
-    if (c < 128) out += fromCharCode(c);
-    else {
-      out += decodeStr(uint8.subarray(pos - 1, end));
-      break;
-    }
-  } while (pos < end);
-  return out;
+  if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+  // Use `TextDecoder` for strings longer than 64 bytes
+  if (len > 64) return decodeStr(uint8.subarray(pos, end));
+  if (pos < sourceEndPos) {
+    // Check if all bytes are ASCII, use `TextDecoder` if not
+    for (let i = pos; i < end; i++) if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+    // String is all ASCII, so slice from `sourceTextLatin`
+    return sourceTextLatin.substr(pos, len);
+  }
+  // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+  // Copy bytes into temp array.
+  // If any byte is non-ASCII, use `TextDecoder`.
+  let arr = stringDecodeArrays[len];
+  for (let i = 0; i < len; i++) {
+    let b = uint8[pos + i];
+    if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+    arr[i] = b;
+  }
+  // Call `fromCharCode` with temp array
+  return fromCharCode.apply(null, arr);
 }

 function deserializeVecComment(pos) {
diff --git a/tasks/ast_tools/src/generators/raw_transfer.rs b/tasks/ast_tools/src/generators/raw_transfer.rs
index 2d0cab965ebf9..94658a3dbbb5a 100644
--- a/tasks/ast_tools/src/generators/raw_transfer.rs
+++ b/tasks/ast_tools/src/generators/raw_transfer.rs
@@ -143,14 +143,26 @@ fn generate_deserializers(
         import {{ comments, initComments }} from '../plugins/comments.js';
         /* END_IF */

-        let uint8, uint32, float64, sourceText, sourceStartPos = 0, firstNonAsciiPos = 0;
+        let uint8, uint32, float64, sourceText, sourceTextLatin,
+            sourceStartPos = 0, sourceEndPos = 0, firstNonAsciiPos = 0;

         let parent = null;
         let getLoc;

         const textDecoder = new TextDecoder('utf-8', {{ ignoreBOM: true }}),
-            decodeStr = textDecoder.decode.bind(textDecoder),
-            {{ fromCharCode }} = String;
+            decodeStr = textDecoder.decode.bind(textDecoder);
+
+        const {{ fromCharCode }} = String,
+            {{ latin1Slice }} = Buffer.prototype;
+
+        const STRING_DECODE_CROSSOVER = 64;
+
+        // Arrays used by `deserializeStr` for passing to `String.fromCharCode`.
+        // These arrays are reused over and over, avoiding allocating a new temporary array for each string.
+        const stringDecodeArrays = new Array(STRING_DECODE_CROSSOVER + 1).fill(null);
+        for (let i = 0; i <= STRING_DECODE_CROSSOVER; i++) {{
+            stringDecodeArrays[i] = new Array(i).fill(0);
+        }}

         /* IF LOC */
         const NodeProto = Object.create(Object.prototype, {{
@@ -166,6 +178,7 @@ fn generate_deserializers(

         /* IF !LINTER */
         export function deserialize(buffer, sourceText, sourceByteLen) {{
+            sourceEndPos = sourceByteLen;
             const data = deserializeWith(buffer, sourceText, sourceByteLen, null, deserializeRawTransferData);
             resetBuffer();
             return data;
@@ -191,22 +204,29 @@ fn generate_deserializers(
             // Find first non-ASCII byte in source region.
             // `sourceText.substr()` can be used for strings which are within source text and ending before
             // this position, since byte offsets equal char offsets in the all-ASCII prefix.
+            // Also decode source text as Latin-1 (or reuse `sourceText` if it's all ASCII).
             if (LINTER) {{
                 if (sourceIsAscii === true) {{
                     firstNonAsciiPos = sourceStartPos + sourceByteLen;
+                    sourceTextLatin = sourceText;
                 }} else {{
                     let i = sourceStartPos;
                     const sourceEndPos = sourceStartPos + sourceByteLen;
                     for (; i < sourceEndPos && uint8[i] < 128; i++);
                     firstNonAsciiPos = i;
+
+                    sourceTextLatin = latin1Slice.call(uint8, sourceStartPos, sourceEndPos);
                 }}
             }} else {{
                 if (sourceIsAscii === true) {{
                     firstNonAsciiPos = sourceByteLen;
+                    sourceTextLatin = sourceText;
                 }} else {{
                     let i = 0;
                     for (; i < sourceByteLen && uint8[i] < 128; i++);
                     firstNonAsciiPos = i;
+
+                    sourceTextLatin = latin1Slice.call(uint8, 0, sourceByteLen);
                 }}
             }}

@@ -216,8 +236,8 @@ fn generate_deserializers(
         }}

         export function resetBuffer() {{
-            // Clear buffer and source text string to allow them to be garbage collected
-            uint8 = uint32 = float64 = sourceText = undefined;
+            // Clear buffer and source text strings to allow them to be garbage collected
+            uint8 = uint32 = float64 = sourceText = sourceTextLatin = undefined;
         }}
     ");

@@ -930,54 +950,70 @@ fn generate_primitive(primitive_def: &PrimitiveDef, code: &mut String, schema: &
 static STR_DESERIALIZER_BODY: &str = "
     const pos32 = pos >> 2,
         len = uint32[pos32 + 2];
+
     if (len === 0) return '';

     pos = uint32[pos32];

     const end = pos + len;

-    if (LINTER) {
-        // Note: Tried reducing this check to a single branch by making the comparison the equivalent of this Rust:
-        // `end.wrapping_sub(sourceStartPos) <= firstNonAsciiOffset`.
-        //
-        // The JS versions tried were:
-        // - `((end - sourceStartPos) >>> 0) <= firstNonAsciiOffset`
-        // - `((end - sourceStartPos) & 0x7FFF_FFFF) <= firstNonAsciiOffset`
-        // But it turned out that these are both slower by 5-10% on files which are all ASCII.
-        //
-        // `>>>` is slower as V8 can't assume result fits in an SMI (which is a 32-bit *signed* integer),
-        // as result could be greater or equal to `2 ** 31`. So it converts both the comparison's operands to `float64`s
-        // and does float compare (which is slower than integer compare).
-        //
-        // `& 0x7FFF_FFFF` is slower as it has a longer chain of data dependencies than the 2 independent
-        // branch comparisons.
-        //
-        // Both branches are very predictable, so 2 branches wins.
-        if (pos >= sourceStartPos && end <= firstNonAsciiPos) {
-            return sourceText.substr(pos - sourceStartPos, len);
-        }
-    } else {
-        if (end <= firstNonAsciiPos) return sourceText.substr(pos, len);
+    /* IF !LINTER */
+    if (end <= firstNonAsciiPos) return sourceTextLatin.substr(pos, len);
+    /* END_IF */
+
+    /* IF LINTER */
+    // Note: Tried reducing this check to a single branch by making the comparison the equivalent of this Rust:
+    // `end.wrapping_sub(sourceStartPos) <= firstNonAsciiOffset`.
+    //
+    // The JS versions tried were:
+    // - `((end - sourceStartPos) >>> 0) <= firstNonAsciiOffset`
+    // - `((end - sourceStartPos) & 0x7FFF_FFFF) <= firstNonAsciiOffset`
+    // But it turned out that these are both slower by 5-10% on files which are all ASCII.
+    //
+    // `>>>` is softer as V8 can't assume result fits in an SMI (which is a 32-bit *signed* integer),
+    // as result could be greater or equal to `2 ** 31`. So it converts both the comparison's operands to `float64`s
+    // and does float compare (which is slower than integer compare).
+    //
+    // `& 0x7FFF_FFFF` is slower as it has a longer chain of data dependencies than the 2 independent
+    // branch comparisons.
+    //
+    // Both branches are very predictable, so 2 branches wins.
+    const isInSourceRegion = pos >= sourceStartPos;
+    if (isInSourceRegion && end <= firstNonAsciiPos) {
+        return sourceTextLatin.substr(pos - sourceStartPos, len);
     }
+    /* END_IF */

-    // Use `TextDecoder` for strings longer than 9 bytes.
-    // For shorter strings, the byte-by-byte loop below avoids native call overhead.
-    if (len > 9) return decodeStr(uint8.subarray(pos, end));
-
-    // Shorter strings decode by hand to avoid native call
-    let out = '',
-        c;
-    do {
-        c = uint8[pos++];
-        if (c < 0x80) {
-            out += fromCharCode(c);
-        } else {
-            out += decodeStr(uint8.subarray(pos - 1, end));
-            break;
+    // Use `TextDecoder` for strings longer than 64 bytes
+    if (len > STRING_DECODE_CROSSOVER) return decodeStr(uint8.subarray(pos, end));
+
+    // If string is in source region, use slice of `sourceTextLatin` if all ASCII
+    /* IF !LINTER */
+    const isInSourceRegion = pos < sourceEndPos;
+    /* END_IF */
+
+    if (isInSourceRegion) {
+        // Check if all bytes are ASCII, use `TextDecoder` if not
+        for (let i = pos; i < end; i++) {
+            if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
         }
-    } while (pos < end);

-    return out;
+        // String is all ASCII, so slice from `sourceTextLatin`
+        return sourceTextLatin.substr(LINTER ? pos - sourceStartPos : pos, len);
+    }
+
+    // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
+    // Copy bytes into temp array.
+    // If any byte is non-ASCII, use `TextDecoder`.
+    const arr = stringDecodeArrays[len];
+    for (let i = 0; i < len; i++) {
+        const b = uint8[pos + i];
+        if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+        arr[i] = b;
+    }
+
+    // Call `fromCharCode` with temp array
+    return fromCharCode.apply(null, arr);
 ";

 /// Generate deserialize function for an `Option`.
PATCH

echo "Patch applied successfully"
