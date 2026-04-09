#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'import_record.kind == .require or import_record.kind == .require_resolve or import_record.kind == .dynamic' src/linker.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the complete patch for all three files
git apply - <<'PATCH'
diff --git a/src/linker.zig b/src/linker.zig
index bae52a8f405..f9ce66257eb 100644
--- a/src/linker.zig
+++ b/src/linker.zig
@@ -222,7 +222,7 @@ pub const Linker = struct {

         if (comptime is_bun) {
             // make these happen at runtime
-            if (import_record.kind == .require or import_record.kind == .require_resolve) {
+            if (import_record.kind == .require or import_record.kind == .require_resolve or import_record.kind == .dynamic) {
                 return false;
             }
         }
diff --git a/src/logger.zig b/src/logger.zig
index 1214403e0a0..ab4f4e053ff 100644
--- a/src/logger.zig
+++ b/src/logger.zig
@@ -927,7 +927,9 @@ pub const Log = struct {
         err: anyerror,
     ) OOM!void {
         @branchHint(.cold);
-        return try addResolveErrorWithLevel(log, source, r, allocator, fmt, args, import_kind, false, .err, err);
+        // Always dupe the line_text from the source to ensure the Location data
+        // outlives the source's backing memory (which may be arena-allocated).
+        return try addResolveErrorWithLevel(log, source, r, allocator, fmt, args, import_kind, true, .err, err);
     }

     pub fn addResolveErrorWithTextDupe(
diff --git a/src/s3/credentials.zig b/src/s3/credentials.zig
index 162b7f18597..d6a8632611b 100644
--- a/src/s3/credentials.zig
+++ b/src/s3/credentials.zig
@@ -1165,7 +1165,7 @@ const CanonicalRequest = struct {
 /// Returns true if the given slice contains any CR (\r) or LF (\n) characters,
 /// which would allow HTTP header injection if used in a header value.
 fn containsNewlineOrCR(value: []const u8) bool {
-    return std.mem.indexOfAny(u8, value, "\r\n") != null;
+    return strings.indexOfAny(value, "\r\n") != null;
 }

 const std = @import("std");
PATCH

echo "Patch applied successfully."
