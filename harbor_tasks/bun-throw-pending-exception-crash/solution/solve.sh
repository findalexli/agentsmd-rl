#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if throwValue already checks hasException, patch is applied
if grep -q 'if (this.hasException()) return error.JSError;' src/bun.js/bindings/JSGlobalObject.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/JSGlobalObject.zig b/src/bun.js/bindings/JSGlobalObject.zig
index 9fd0ed7e7e0..e410a266eba 100644
--- a/src/bun.js/bindings/JSGlobalObject.zig
+++ b/src/bun.js/bindings/JSGlobalObject.zig
@@ -51,6 +51,10 @@ pub const JSGlobalObject = opaque {

     pub fn throwTODO(this: *JSGlobalObject, msg: []const u8) bun.JSError {
         const err = this.createErrorInstance("{s}", .{msg});
+        if (err == .zero) {
+            bun.assert(this.hasException());
+            return error.JSError;
+        }
         err.put(this, ZigString.static("name"), (bun.String.static("TODOError").toJS(this)) catch return error.JSError);
         return this.throwValue(err);
     }
@@ -373,6 +377,10 @@ pub const JSGlobalObject = opaque {

     pub fn createRangeError(this: *JSGlobalObject, comptime fmt: [:0]const u8, args: anytype) JSValue {
         const err = createErrorInstance(this, fmt, args);
+        if (err == .zero) {
+            bun.assert(this.hasException());
+            return .zero;
+        }
         err.put(this, ZigString.static("code"), ZigString.static(@tagName(jsc.Node.ErrorCode.ERR_OUT_OF_RANGE)).toJS(this));
         return err;
     }
@@ -393,6 +401,10 @@ pub const JSGlobalObject = opaque {
         args: anytype,
     ) JSError {
         const err = createErrorInstance(this, message, args);
+        if (err == .zero) {
+            bun.assert(this.hasException());
+            return error.JSError;
+        }
         err.put(this, ZigString.static("code"), ZigString.init(@tagName(opts.code)).toJS(this));
         if (opts.name) |name| err.put(this, ZigString.static("name"), ZigString.init(name).toJS(this));
         if (opts.errno) |errno| err.put(this, ZigString.static("errno"), try .fromAny(this, i32, errno));
@@ -405,7 +417,10 @@ pub const JSGlobalObject = opaque {
     /// chances are you should be using `.ERR(...).throw()` instead.
     pub fn throw(this: *JSGlobalObject, comptime fmt: [:0]const u8, args: anytype) JSError {
         const instance = this.createErrorInstance(fmt, args);
-        bun.assert(instance != .zero);
+        if (instance == .zero) {
+            bun.assert(this.hasException());
+            return error.JSError;
+        }
         return this.throwValue(instance);
     }

@@ -413,7 +428,10 @@ pub const JSGlobalObject = opaque {
         const instance = switch (Output.enable_ansi_colors_stderr) {
             inline else => |enabled| this.createErrorInstance(Output.prettyFmt(fmt, enabled), args),
         };
-        bun.assert(instance != .zero);
+        if (instance == .zero) {
+            bun.assert(this.hasException());
+            return error.JSError;
+        }
         return this.throwValue(instance);
     }

@@ -454,6 +472,10 @@ pub const JSGlobalObject = opaque {
     }

     pub fn throwValue(this: *JSGlobalObject, value: jsc.JSValue) JSError {
+        // A termination exception (e.g. stack overflow) may already be
+        // pending. Don't try to override it — that would hit
+        // releaseAssertNoException in VM.throwError.
+        if (this.hasException()) return error.JSError;
         return this.vm().throwError(this, value);
     }

@@ -484,7 +506,7 @@ pub const JSGlobalObject = opaque {
         defer allocator_.free(buffer);
         const str = ZigString.initUTF8(buffer);
         const err_value = str.toErrorInstance(this);
-        return this.vm().throwError(this, err_value);
+        return this.throwValue(err_value);
     }

     // TODO: delete these two fns

PATCH

echo "Patch applied successfully."
