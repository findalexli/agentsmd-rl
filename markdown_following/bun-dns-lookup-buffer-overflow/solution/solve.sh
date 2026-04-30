#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'stackFallback(1024, bun.default_allocator)' src/bun.js/api/bun/dns.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/bun.js/api/bun/dns.zig b/src/bun.js/api/bun/dns.zig
index 9eeac304f2c..21255d52397 100644
--- a/src/bun.js/api/bun/dns.zig
+++ b/src/bun.js/api/bun/dns.zig
@@ -68,11 +68,10 @@ const LibInfo = struct {
             return dns_lookup.promise.value();
         }

-        var name_buf: [1024]u8 = undefined;
-        _ = strings.copy(name_buf[0..], query.name);
-
-        name_buf[query.name.len] = 0;
-        const name_z = name_buf[0..query.name.len :0];
+        var stack_fallback = std.heap.stackFallback(1024, bun.default_allocator);
+        const name_allocator = stack_fallback.get();
+        const name_z = bun.handleOom(name_allocator.dupeZ(u8, query.name));
+        defer name_allocator.free(name_z);

         var request = GetAddrInfoRequest.init(
             cache,

PATCH

echo "Patch applied successfully."
