#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency: check if the fix is already applied
if grep -q 'package_manager.*pm\.log = &log' src/bun.js/VirtualMachine.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/VirtualMachine.zig b/src/bun.js/VirtualMachine.zig
index 3512d374025..2475cf4c275 100644
--- a/src/bun.js/VirtualMachine.zig
+++ b/src/bun.js/VirtualMachine.zig
@@ -1836,10 +1836,16 @@ pub fn resolveMaybeNeedsTrailingSlash(
     jsc_vm.log = &log;
     jsc_vm.transpiler.resolver.log = &log;
     jsc_vm.transpiler.linker.log = &log;
+    if (jsc_vm.transpiler.resolver.package_manager) |pm| {
+        pm.log = &log;
+    }
     defer {
         jsc_vm.log = old_log;
         jsc_vm.transpiler.linker.log = old_log;
         jsc_vm.transpiler.resolver.log = old_log;
+        if (jsc_vm.transpiler.resolver.package_manager) |pm| {
+            pm.log = old_log;
+        }
     }
     jsc_vm._resolve(&result, specifier_utf8.slice(), normalizeSource(source_utf8.slice()), is_esm, is_a_file_path) catch |err_| {
         var err = err_;

PATCH

echo "Patch applied successfully."
