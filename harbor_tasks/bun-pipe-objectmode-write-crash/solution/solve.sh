#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line from the fix)
if grep -q 'dest.destroy(err)' src/js/internal/streams/readable.ts; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/js/internal/streams/readable.ts b/src/js/internal/streams/readable.ts
index 70044abd4fb..67fb16b260c 100644
--- a/src/js/internal/streams/readable.ts
+++ b/src/js/internal/streams/readable.ts
@@ -912,10 +912,14 @@ Readable.prototype.pipe = function (dest, pipeOpts) {
   src.on("data", ondata);
   function ondata(chunk) {
     $debug("ondata");
-    const ret = dest.write(chunk);
-    $debug("dest.write", ret);
-    if (ret === false) {
-      pause();
+    try {
+      const ret = dest.write(chunk);
+      $debug("dest.write", ret);
+      if (ret === false) {
+        pause();
+      }
+    } catch (err) {
+      dest.destroy(err);
     }
   }

PATCH
