#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied
if grep -q 'new_lm_head._is_hf_initialized = True' src/transformers/modeling_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/src/transformers/modeling_utils.py b/src/transformers/modeling_utils.py
index f50774ef8065..e3e5021e5020 100644
--- a/src/transformers/modeling_utils.py
+++ b/src/transformers/modeling_utils.py
@@ -2983,6 +2983,7 @@ def _get_resized_lm_head(
                 new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias
             )

+        new_lm_head._is_hf_initialized = True
         return new_lm_head

     def _init_added_embeddings_weights_with_mean(
PATCH

echo "Patch applied successfully."
