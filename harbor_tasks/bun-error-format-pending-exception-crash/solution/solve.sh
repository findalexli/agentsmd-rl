#!/usr/bin/env bash
set -euo pipefail

cd /repo

TARGET="src/bun.js/bindings/JSGlobalObject.zig"

# Idempotency: check if the fix is already applied
if grep -q 'clearExceptionExceptTermination' "$TARGET" | head -1 | grep -q 'catch {'; then
  echo "Fix already applied."
  exit 0
fi

# Count existing clearExceptionExceptTermination calls — if more than the original 7, likely already patched
EXISTING_COUNT=$(grep -c 'clearExceptionExceptTermination' "$TARGET" || true)
if [ "$EXISTING_COUNT" -gt 7 ]; then
  echo "Fix appears already applied ($EXISTING_COUNT clearExceptionExceptTermination calls found)."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/JSGlobalObject.zig b/src/bun.js/bindings/JSGlobalObject.zig
index 3927003a04e..9fd0ed7e7e0 100644
--- a/src/bun.js/bindings/JSGlobalObject.zig
+++ b/src/bun.js/bindings/JSGlobalObject.zig
@@ -286,9 +286,12 @@ pub const JSGlobalObject = opaque {
             var buf = std.Io.Writer.Allocating.initCapacity(stack_fallback.get(), 2048) catch unreachable;
             defer buf.deinit();
             var writer = &buf.writer;
-            writer.print(fmt, args) catch
-                // if an exception occurs in the middle of formatting the error message, it's better to just return the formatting string than an error about an error
+            writer.print(fmt, args) catch {
+                // if an exception occurs in the middle of formatting the error message, it's better to just return the formatting string than an error about an error.
+                // Clear any pending JS exception (e.g. from Symbol.toPrimitive) so that throwValue doesn't hit assertNoException.
+                _ = this.clearExceptionExceptTermination();
                 return ZigString.static(fmt).toErrorInstance(this);
+            };

             // Ensure we clone it.
             var str = ZigString.initUTF8(buf.written());
@@ -309,7 +312,10 @@ pub const JSGlobalObject = opaque {
             var buf = bun.MutableString.init2048(stack_fallback.get()) catch unreachable;
             defer buf.deinit();
             var writer = buf.writer();
-            writer.print(fmt, args) catch return ZigString.static(fmt).toErrorInstance(this);
+            writer.print(fmt, args) catch {
+                _ = this.clearExceptionExceptTermination();
+                return ZigString.static(fmt).toTypeErrorInstance(this);
+            };
             var str = ZigString.fromUTF8(buf.slice());
             return str.toTypeErrorInstance(this);
         } else {
@@ -337,7 +343,10 @@ pub const JSGlobalObject = opaque {
             var buf = bun.MutableString.init2048(stack_fallback.get()) catch unreachable;
             defer buf.deinit();
             var writer = buf.writer();
-            writer.print(fmt, args) catch return ZigString.static(fmt).toErrorInstance(this);
+            writer.print(fmt, args) catch {
+                _ = this.clearExceptionExceptTermination();
+                return ZigString.static(fmt).toSyntaxErrorInstance(this);
+            };
             var str = ZigString.fromUTF8(buf.slice());
             return str.toSyntaxErrorInstance(this);
         } else {
@@ -351,7 +360,10 @@ pub const JSGlobalObject = opaque {
             var buf = bun.MutableString.init2048(stack_fallback.get()) catch unreachable;
             defer buf.deinit();
             var writer = buf.writer();
-            writer.print(fmt, args) catch return ZigString.static(fmt).toErrorInstance(this);
+            writer.print(fmt, args) catch {
+                _ = this.clearExceptionExceptTermination();
+                return ZigString.static(fmt).toRangeErrorInstance(this);
+            };
             var str = ZigString.fromUTF8(buf.slice());
             return str.toRangeErrorInstance(this);
         } else {

PATCH

echo "Patch applied successfully."
