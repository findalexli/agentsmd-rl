#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q '&|<>^!()' ext/node/polyfills/internal/child_process.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/ext/node/polyfills/internal/child_process.ts b/ext/node/polyfills/internal/child_process.ts
index 02e8eef61e0084..987953bae7e56a 100644
--- a/ext/node/polyfills/internal/child_process.ts
+++ b/ext/node/polyfills/internal/child_process.ts
@@ -1279,7 +1279,10 @@ function escapeShellArg(arg: string): string {
       return '""';
     }
     // If no special characters, return as-is
-    if (!/[\s"\\]/.test(arg)) {
+    // Must include cmd.exe metacharacters: &|<>^!()
+    // Note: % is not included because cmd.exe expands %VAR% even inside
+    // double quotes and there is no reliable escape for it outside batch files.
+    if (!/[\s"\\&|<>^!()]/.test(arg)) {
       return arg;
     }
     // Escape backslashes before quotes, then escape quotes

PATCH

echo "Patch applied successfully."
