#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency: check if the fix is already applied
if grep -q 'if (entry.refcount == 0)' src/bun.js/api/bun/dns.zig 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/api/bun/dns.zig b/src/bun.js/api/bun/dns.zig
index 6c8ee6c99c2..eed1fcb0441 100644
--- a/src/bun.js/api/bun/dns.zig
+++ b/src/bun.js/api/bun/dns.zig
@@ -1227,7 +1227,7 @@ pub const internal = struct {
         can_retry_for_addrconfig: bool = default_hints.flags.ADDRCONFIG,

         pub fn isExpired(this: *Request, timestamp_to_store: *u32) bool {
-            if (this.refcount > 0 or this.result == null) {
+            if (this.result == null) {
                 return false;
             }

@@ -1284,9 +1284,11 @@ pub const internal = struct {
                 if (entry.key.hash == key.hash and entry.valid) {
                     if (entry.isExpired(timestamp_to_store)) {
                         log("get: expired entry", .{});
-                        _ = this.deleteEntryAt(len, i);
-                        entry.deinit();
-                        len = this.len;
+                        if (entry.refcount == 0) {
+                            _ = this.deleteEntryAt(len, i);
+                            entry.deinit();
+                            len = this.len;
+                        }
                         continue;
                     }

@@ -1789,7 +1791,9 @@ pub const internal = struct {
         global_cache.lock.lock();
         defer global_cache.lock.unlock();

-        req.valid = err == 0;
+        if (err != 0) {
+            req.valid = false;
+        }
         dns_cache_errors += @as(usize, @intFromBool(err != 0));

         bun.assert(req.refcount > 0);

PATCH

echo "Fix applied successfully."
