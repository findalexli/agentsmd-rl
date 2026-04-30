#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

TARGET="src/js/builtins/ProcessObjectInternals.ts"

# Idempotency check: see if _final is already defined
if grep -q 'stream\._final' "$TARGET"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/js/builtins/ProcessObjectInternals.ts b/src/js/builtins/ProcessObjectInternals.ts
index 67156abc569..7f3d1d22de3 100644
--- a/src/js/builtins/ProcessObjectInternals.ts
+++ b/src/js/builtins/ProcessObjectInternals.ts
@@ -80,6 +80,26 @@ export function getStdioWriteStream(
         });
       }
     };
+
+    const kFastPath = require("internal/fs/streams").kWriteStreamFastPath;
+    stream._final = function (cb) {
+      try {
+        const sink = this[kFastPath];
+        if (sink && sink !== true) {
+          const result = sink.flush();
+          if ($isPromise(result)) {
+            result.then(
+              () => cb(null),
+              err => cb(err),
+            );
+            return;
+          }
+        }
+        cb(null);
+      } catch (err) {
+        cb(err);
+      }
+    };
   }

   stream._isStdio = true;

PATCH

echo "Patch applied successfully."
