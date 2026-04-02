#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Check if already applied
if grep -q 'get_sliding_window() == 0' vllm/config/model.py 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/config/model.py b/vllm/config/model.py
index e51723009618..e934ff554437 100644
--- a/vllm/config/model.py
+++ b/vllm/config/model.py
@@ -586,6 +586,14 @@ def __post_init__(
             config_format=self.config_format,
         )

+        # Some checkpoints set sliding_window to 0 to indicate that sliding window is
+        # disabled, but vLLM uses None for that. Convert 0 to None to avoid errors.
+        # Set before get_and_verify_max_len to ensure that max_model_len does not get
+        # capped to 0.
+        if self.get_sliding_window() == 0:
+            self.disable_sliding_window = True
+            self.hf_text_config.sliding_window = None
+
         self.original_max_model_len = self.max_model_len
         self.max_model_len = self.get_and_verify_max_len(self.max_model_len)

PATCH

echo "Patch applied successfully"
