#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line from the fix)
if grep -q '!value.isObject()' src/bun.js/api/ffi.zig; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/api/ffi.zig b/src/bun.js/api/ffi.zig
index bf5b35d0311..6f4ec414336 100644
--- a/src/bun.js/api/ffi.zig
+++ b/src/bun.js/api/ffi.zig
@@ -960,6 +960,9 @@ pub const FFI = struct {
             for (symbols.keys()) |key| {
                 allocator.free(@constCast(key));
             }
+            for (symbols.values()) |*function_| {
+                function_.arg_types.deinit(allocator);
+            }
             symbols.clearAndFree(allocator);
             return val;
         }
@@ -1052,6 +1055,9 @@ pub const FFI = struct {
             for (symbols.keys()) |key| {
                 bun.default_allocator.free(@constCast(key));
             }
+            for (symbols.values()) |*function_| {
+                function_.arg_types.deinit(bun.default_allocator);
+            }
             symbols.clearAndFree(bun.default_allocator);
             return val;
         }
@@ -1195,6 +1201,9 @@ pub const FFI = struct {
             for (symbols.keys()) |key| {
                 allocator.free(@constCast(key));
             }
+            for (symbols.values()) |*function_| {
+                function_.arg_types.deinit(allocator);
+            }
             symbols.clearAndFree(allocator);
             return val;
         }
@@ -1411,7 +1420,7 @@ pub const FFI = struct {
         while (try symbols_iter.next()) |prop| {
             const value = symbols_iter.value;

-            if (value.isEmptyOrUndefinedOrNull()) {
+            if (value.isEmptyOrUndefinedOrNull() or !value.isObject()) {
                 return global.toTypeError(.INVALID_ARG_VALUE, "Expected an object for key \"{f}\"", .{prop});
             }

PATCH
