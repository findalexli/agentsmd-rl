#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: skip if fix is already applied
if grep -q 'if not name and ext:' client/python/gradio_client/utils.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/client/python/gradio_client/utils.py b/client/python/gradio_client/utils.py
index e4c2e9dbe0..9277099fc8 100644
--- a/client/python/gradio_client/utils.py
+++ b/client/python/gradio_client/utils.py
@@ -746,6 +746,11 @@ def strip_invalid_filename_characters(filename: str, max_bytes: int = 200) -> st
         ext = "." + "".join(
             [char for char in ext[1:] if char.isalnum() or char in "._-"]
         )
+    # If the stem was stripped entirely but an extension exists, use a
+    # fallback name so that the extension is not mistaken for a dotfile
+    # stem (e.g. "#.txt" → ".txt" → Path(".txt").suffix == "").
+    if not name and ext:
+        name = "file"
     filename = name + ext
     filename_len = len(filename.encode())
     if filename_len > max_bytes:

PATCH

echo "Patch applied successfully."
