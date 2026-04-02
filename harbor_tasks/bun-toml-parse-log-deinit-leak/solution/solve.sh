#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied
if grep -q 'defer log.deinit()' src/bun.js/api/TOMLObject.zig; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/api/TOMLObject.zig b/src/bun.js/api/TOMLObject.zig
index 6300e216b49..b65bd608a71 100644
--- a/src/bun.js/api/TOMLObject.zig
+++ b/src/bun.js/api/TOMLObject.zig
@@ -28,12 +28,13 @@ pub fn parse(
     defer ast_scope.exit();

     var log = logger.Log.init(default_allocator);
-    const arguments = callframe.arguments_old(1).slice();
-    if (arguments.len == 0 or arguments[0].isEmptyOrUndefinedOrNull()) {
+    defer log.deinit();
+    const input_value = callframe.argument(0);
+    if (input_value.isEmptyOrUndefinedOrNull()) {
         return globalThis.throwInvalidArguments("Expected a string to parse", .{});
     }

-    var input_slice = try arguments[0].toSlice(globalThis, bun.default_allocator);
+    var input_slice = try input_value.toSlice(globalThis, bun.default_allocator);
     defer input_slice.deinit();
     const source = &logger.Source.initPathString("input.toml", input_slice.slice());
     const parse_result = TOML.parse(source, &log, allocator, false) catch |err| {

PATCH

echo "Patch applied successfully."
