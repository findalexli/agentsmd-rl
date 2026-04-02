#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'except (NameError, TypeError)' gradio/utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/utils.py b/gradio/utils.py
index 327dbf8b4d..61bac0b8f9 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -1140,7 +1140,10 @@ def get_type_hints(fn):
         fn = fn.__call__
     else:
         return {}
-    return typing.get_type_hints(fn)
+    try:
+        return typing.get_type_hints(fn)
+    except (NameError, TypeError):
+        return {}


 def is_special_typed_parameter(name, parameter_types):

PATCH

echo "Patch applied successfully."
