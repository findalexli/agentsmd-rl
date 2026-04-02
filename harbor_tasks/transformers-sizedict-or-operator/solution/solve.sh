#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied
if grep -q '__or__' src/transformers/image_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/image_utils.py b/src/transformers/image_utils.py
index 1691a485d3b4..0312bec9cea6 100644
--- a/src/transformers/image_utils.py
+++ b/src/transformers/image_utils.py
@@ -1001,3 +1001,17 @@ def __eq__(self, other):
                 getattr(other, f.name) for f in fields(self)
             )
         return NotImplemented
+
+    def __or__(self, other) -> "SizeDict":
+        if isinstance(other, dict | SizeDict):
+            merged = dict(self)
+            merged.update(dict(other))
+            return SizeDict(**merged)
+        return NotImplemented
+
+    def __ror__(self, other) -> dict:
+        if isinstance(other, dict):
+            merged = dict(other)
+            merged.update(dict(self))
+            return merged
+        return NotImplemented

PATCH

echo "Patch applied successfully."
