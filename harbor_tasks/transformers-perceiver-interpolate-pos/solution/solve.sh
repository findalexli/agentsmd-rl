#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Idempotent: check if patch is already applied
# In fixed code, the interpolate call uses (height, width) not (new_height, new_width)
if grep -A2 'nn.functional.interpolate' src/transformers/models/perceiver/modeling_perceiver.py | grep -q 'size=(height, width)'; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn - <<'PATCH'
diff --git a/src/transformers/models/perceiver/modeling_perceiver.py b/src/transformers/models/perceiver/modeling_perceiver.py
index 531d5c364805..6b2850390e27 100755
--- a/src/transformers/models/perceiver/modeling_perceiver.py
+++ b/src/transformers/models/perceiver/modeling_perceiver.py
@@ -2567,7 +2567,7 @@ def interpolate_pos_encoding(self, position_embeddings: torch.Tensor, height: in

         position_embeddings = nn.functional.interpolate(
             position_embeddings,
-            size=(new_height, new_width),
+            size=(height, width),
             mode="bicubic",
             align_corners=False,
         )
PATCH
