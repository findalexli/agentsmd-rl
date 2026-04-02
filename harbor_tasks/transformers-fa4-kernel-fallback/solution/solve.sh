#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Check if already applied: FA4 entry in FLASH_ATTN_KERNEL_FALLBACK dict
# (must check near the dict, not just anywhere — "flash_attention_4" exists elsewhere in the file)
if grep -A5 'FLASH_ATTN_KERNEL_FALLBACK' src/transformers/modeling_flash_attention_utils.py | grep -q '"flash_attention_4"'; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/modeling_flash_attention_utils.py b/src/transformers/modeling_flash_attention_utils.py
index c5b5b6246c6c..9211ccb19a9e 100644
--- a/src/transformers/modeling_flash_attention_utils.py
+++ b/src/transformers/modeling_flash_attention_utils.py
@@ -62,6 +62,7 @@ def is_flash_attn_available():
 FLASH_ATTN_KERNEL_FALLBACK = {
     "flash_attention_2": "kernels-community/flash-attn2",
     "flash_attention_3": "kernels-community/vllm-flash-attn3",
+    "flash_attention_4": "kernels-community/flash-attn4",
 }


diff --git a/src/transformers/modeling_utils.py b/src/transformers/modeling_utils.py
index ff56e2db03ac..1cdb033cb709 100644
--- a/src/transformers/modeling_utils.py
+++ b/src/transformers/modeling_utils.py
@@ -1814,10 +1814,6 @@ def _check_and_adjust_attn_implementation(
         if is_flash_attention_requested(requested_attention_implementation=attn_implementation):
             # If FA not installed, do not fail but use kernels instead if possible
             for fa_version in FLASH_ATTENTION_COMPATIBILITY_MATRIX.keys():
-                # No kernels support for FA4 for now
-                if fa_version == 4:
-                    continue
-
                 # Check whether we have an original FA requested but not available in the env
                 if requested_original_flash_attn := (
                     attn_implementation.removeprefix("paged|") == f"flash_attention_{fa_version}"

PATCH

echo "Patch applied successfully."
