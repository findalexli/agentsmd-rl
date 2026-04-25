#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied
if grep -q 'putMayBeIndex' src/bun.js/test/expect.zig; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/test/expect.zig b/src/bun.js/test/expect.zig
index ffa8303115a..79d9b5f7e54 100644
--- a/src/bun.js/test/expect.zig
+++ b/src/bun.js/test/expect.zig
@@ -957,9 +957,9 @@ pub const Expect = struct {

                 const wrapper_fn = Bun__JSWrappingFunction__create(globalThis, matcher_name, jsc.toJSHostFn(Expect.applyCustomMatcher), matcher_fn, true);

-                expect_proto.put(globalThis, matcher_name, wrapper_fn);
-                expect_constructor.put(globalThis, matcher_name, wrapper_fn);
-                expect_static_proto.put(globalThis, matcher_name, wrapper_fn);
+                try expect_proto.putMayBeIndex(globalThis, matcher_name, wrapper_fn);
+                try expect_constructor.putMayBeIndex(globalThis, matcher_name, wrapper_fn);
+                try expect_static_proto.putMayBeIndex(globalThis, matcher_name, wrapper_fn);
             }
         }

PATCH

echo "Patch applied successfully."
