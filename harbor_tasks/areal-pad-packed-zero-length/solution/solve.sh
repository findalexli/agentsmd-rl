#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency: check if fix is already applied
if grep -q 'elif pad_length == 0:' areal/utils/data.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/utils/data.py b/areal/utils/data.py
index 392f7d246..834ea23e9 100644
--- a/areal/utils/data.py
+++ b/areal/utils/data.py
@@ -917,6 +917,13 @@ def pad_packed_tensor_dict(
         raise ValueError(
             f"pad_to_length {pad_to_length} is smaller than total length {total_length}."
         )
+    elif pad_length == 0:
+        return (
+            data,
+            pad_length,
+            old_cu_seqlens,
+            align_to_length,
+        )
     new_cu_seqlens = F.pad(cu_seqlens, (0, 1), value=pad_to_length)
     new_max_seqlen = max(max_seqlen, pad_length)
     padded_data = {}

PATCH

echo "Patch applied successfully."
