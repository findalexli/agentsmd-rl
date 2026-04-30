#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied
if grep -q '_patch_is_base_mistral_in_ci' python/sglang/srt/utils/hf_transformers_utils.py 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/utils/hf_transformers_utils.py b/python/sglang/srt/utils/hf_transformers_utils.py
index 318b2e18649f..faf43db97556 100644
--- a/python/sglang/srt/utils/hf_transformers_utils.py
+++ b/python/sglang/srt/utils/hf_transformers_utils.py
@@ -712,6 +712,49 @@ def filter(self, record: logging.LogRecord) -> bool:
         return "Calling super().encode with" not in record.getMessage()


+_is_base_mistral_patched = False
+
+# transformers version where is_base_mistral calls model_info() on every tokenizer load
+_TRANSFORMERS_PATCHED_VERSION = "5.3.0"
+
+
+def _patch_is_base_mistral_in_ci():
+    """Patch transformers' is_base_mistral to avoid HF API calls in CI.
+
+    transformers calls model_info() inside _patch_mistral_regex -> is_base_mistral
+    for every tokenizer load, which hits HF API even with HF_HUB_OFFLINE=1.
+    In CI this exhausts the 3000 req/5min rate limit and causes 429 errors.
+    """
+    global _is_base_mistral_patched
+    if _is_base_mistral_patched:
+        return
+
+    from sglang.srt.environ import envs
+
+    if not envs.SGLANG_IS_IN_CI.get():
+        return
+
+    import transformers
+
+    if transformers.__version__ != _TRANSFORMERS_PATCHED_VERSION:
+        logger.warning(
+            "transformers version changed to %s (expected %s), "
+            "is_base_mistral patch skipped — may need update if 429 errors recur",
+            transformers.__version__,
+            _TRANSFORMERS_PATCHED_VERSION,
+        )
+        _is_base_mistral_patched = True  # don't warn repeatedly
+        return
+
+    import transformers.tokenization_utils_tokenizers as tut
+
+    if hasattr(tut, "is_base_mistral"):
+        tut.is_base_mistral = lambda *a, **kw: False
+        logger.info("CI: patched is_base_mistral to skip HF API calls")
+
+    _is_base_mistral_patched = True
+
+
 def get_tokenizer(
     tokenizer_name: str,
     *args,
@@ -755,6 +798,8 @@ def get_tokenizer(
         client.pull_files(ignore_pattern=["*.pt", "*.safetensors", "*.bin"])
         tokenizer_name = client.get_local_dir()

+    _patch_is_base_mistral_in_ci()
+
     try:
         tokenizer = AutoTokenizer.from_pretrained(
             tokenizer_name,

PATCH

echo "Patch applied successfully"
