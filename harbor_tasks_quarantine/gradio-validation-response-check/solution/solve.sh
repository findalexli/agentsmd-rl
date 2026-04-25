#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'isinstance(validation_response, dict)' gradio/queueing.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/queueing.py b/gradio/queueing.py
index 7711ffc1e9..3ac0bc4f10 100644
--- a/gradio/queueing.py
+++ b/gradio/queueing.py
@@ -1014,8 +1014,8 @@ def process_validation_response(
                 validation_data.append({"is_valid": True, "message": ""})

     elif (
-        isinstance(validation_data, dict)
-        and validation_data.get("is_valid", None) is False
+        isinstance(validation_response, dict)
+        and validation_response.get("is_valid", None) is False
     ):
         validation_data.append(
             validation_response,

PATCH

echo "Patch applied successfully."
