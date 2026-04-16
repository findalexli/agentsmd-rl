#!/bin/bash
set -e

cd /workspace/oxc

# Check if already applied (idempotency check)
if grep -q "utf8Slice, latin1Slice" tasks/ast_tools/src/generators/raw_transfer.rs 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

cat > /tmp/fix.patch << 'PATCH'
diff --git a/tasks/ast_tools/src/generators/raw_transfer.rs b/tasks/ast_tools/src/generators/raw_transfer.rs
index 0dd16d824b..08f8b4b5ab 100644
--- a/tasks/ast_tools/src/generators/raw_transfer.rs
+++ b/tasks/ast_tools/src/generators/raw_transfer.rs
@@ -146,11 +146,8 @@ fn generate_deserializers(
         let parent = null;
         let getLoc;

-        const textDecoder = new TextDecoder('utf-8', {{ ignoreBOM: true }}),
-            decodeStr = textDecoder.decode.bind(textDecoder);
-
         const {{ fromCharCode }} = String,
-            {{ latin1Slice }} = Buffer.prototype;
+            {{ utf8Slice, latin1Slice }} = Buffer.prototype;

         const STRING_DECODE_CROSSOVER = 64;

@@ -981,18 +978,18 @@ static STR_DESERIALIZER_BODY: &str = "
     }
     /* END_IF */

-    // Use `TextDecoder` for strings longer than 64 bytes
-    if (len > STRING_DECODE_CROSSOVER) return decodeStr(uint8.subarray(pos, end));
+    // Use `utf8Slice` for strings longer than 64 bytes
+    if (len > STRING_DECODE_CROSSOVER) return utf8Slice.call(uint8, pos, end);

     // If string is in source region, use slice of `sourceTextLatin` if all ASCII
     /* IF !LINTER */
     const isInSourceRegion = pos < sourceEndPos;
     /* END_IF */

     if (isInSourceRegion) {
-        // Check if all bytes are ASCII, use `TextDecoder` if not
+        // Check if all bytes are ASCII, use `utf8Slice` if not
         for (let i = pos; i < end; i++) {
-            if (uint8[i] >= 128) return decodeStr(uint8.subarray(pos, end));
+            if (uint8[i] >= 128) return utf8Slice.call(uint8, pos, end);
         }

         // String is all ASCII, so slice from `sourceTextLatin`
@@ -1001,11 +998,11 @@ static STR_DESERIALIZER_BODY: &str = "

     // String is not in source region - use `fromCharCode.apply` with a temp array of correct length.
     // Copy bytes into temp array.
-    // If any byte is non-ASCII, use `TextDecoder`.
+    // If any byte is non-ASCII, use `utf8Slice`.
     const arr = stringDecodeArrays[len];
     for (let i = 0; i < len; i++) {
         const b = uint8[pos + i];
-        if (b >= 128) return decodeStr(uint8.subarray(pos, end));
+        if (b >= 128) return utf8Slice.call(uint8, pos, end);
         arr[i] = b;
     }
 ";
PATCH

# Apply the patch for raw_transfer.rs
cd /workspace/oxc
patch -p1 < /tmp/fix.patch || true

# Also directly update the generated JS files (since the generator may need dependencies)
# Update all generated JS files with the same change pattern
for file in napi/parser/src-js/generated/deserialize/js.js \
            napi/parser/src-js/generated/deserialize/js_parent.js \
            napi/parser/src-js/generated/deserialize/js_range.js \
            napi/parser/src-js/generated/deserialize/js_range_parent.js \
            napi/parser/src-js/generated/deserialize/ts.js \
            napi/parser/src-js/generated/deserialize/ts_parent.js \
            napi/parser/src-js/generated/deserialize/ts_range.js \
            napi/parser/src-js/generated/deserialize/ts_range_parent.js \
            apps/oxlint/src-js/generated/deserialize.js; do
    if [ -f "$file" ]; then
        # Replace textDecoder/decodeStr declarations with utf8Slice in Buffer.prototype destructuring
        sed -i 's/const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),\n  decodeStr = textDecoder.decode.bind(textDecoder),\n  { fromCharCode } = String,\n  { latin1Slice } = Buffer.prototype,/const { fromCharCode } = String,\n  { utf8Slice, latin1Slice } = Buffer.prototype,/g' "$file" || true
        sed -i 's/const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true }),/const { utf8Slice } = Buffer.prototype;/g' "$file" || true
        sed -i 's/decodeStr = textDecoder.decode.bind(textDecoder),//g' "$file" || true
        sed -i 's/{ latin1Slice } = Buffer.prototype/{ utf8Slice, latin1Slice } = Buffer.prototype/g' "$file" || true
        # Replace decodeStr calls with utf8Slice.call
        sed -i 's/decodeStr(uint8.subarray(pos, end))/utf8Slice.call(uint8, pos, end)/g' "$file" || true
        # Update comments
        sed -i 's/Use `TextDecoder`/Use `utf8Slice`/g' "$file" || true
        sed -i 's/use `TextDecoder`/use `utf8Slice`/g' "$file" || true
    fi
done

# Update apps/oxlint/src-js/plugins/source_code.ts
file="apps/oxlint/src-js/plugins/source_code.ts"
if [ -f "$file" ]; then
    sed -i 's/\/\/ Text decoder, for decoding source text from buffer/const { utf8Slice } = Buffer.prototype;/g' "$file" || true
    sed -i 's/const textDecoder = new TextDecoder("utf-8", { ignoreBOM: true });/const { utf8Slice } = Buffer.prototype;/g' "$file" || true
    sed -i 's/textDecoder.decode(buffer.subarray(sourceStartPos, sourceStartPos + sourceByteLen))/utf8Slice.call(buffer, sourceStartPos, sourceStartPos + sourceByteLen)/g' "$file" || true
fi

echo "Fix applied successfully"
