#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line from the fix)
if grep -q 'arguments.ptr\[1\]\.isObject()' src/bun.js/api/bun/dns.zig; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/api/bun/dns.zig b/src/bun.js/api/bun/dns.zig
index eed1fcb0441..9eeac304f2c 100644
--- a/src/bun.js/api/bun/dns.zig
+++ b/src/bun.js/api/bun/dns.zig
@@ -2719,7 +2719,7 @@ pub const Resolver = struct {
         var options = GetAddrInfo.Options{};
         var port: u16 = 0;

-        if (arguments.len > 1 and arguments.ptr[1].isCell()) {
+        if (arguments.len > 1 and arguments.ptr[1].isObject()) {
             const optionsObject = arguments.ptr[1];

             if (try optionsObject.getTruthy(globalThis, "port")) |port_value| {

PATCH
