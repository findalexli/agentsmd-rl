#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line: range check on float before @intFromFloat)
if grep -q 'float > @as(f64, @floatFromInt(std.math.maxInt(i32)))' src/fd.zig; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/fd.zig b/src/fd.zig
index 6c3ea0e7792..d7c969c84d7 100644
--- a/src/fd.zig
+++ b/src/fd.zig
@@ -331,10 +331,10 @@ pub const FD = packed struct(backing_int) {
         if (@mod(float, 1) != 0) {
             return global.throwRangeError(float, .{ .field_name = "fd", .msg = "an integer" });
         }
-        const int: i64 = @intFromFloat(float);
-        if (int < 0 or int > std.math.maxInt(i32)) {
-            return global.throwRangeError(int, .{ .field_name = "fd", .min = 0, .max = std.math.maxInt(i32) });
+        if (float < 0 or float > @as(f64, @floatFromInt(std.math.maxInt(i32)))) {
+            return global.throwRangeError(float, .{ .field_name = "fd", .min = 0, .max = std.math.maxInt(i32) });
         }
+        const int: i64 = @intFromFloat(float);
         const fd: c_int = @intCast(int);
         if (os == .windows) {
             if (Stdio.fromInt(fd)) |stdio| {

PATCH
