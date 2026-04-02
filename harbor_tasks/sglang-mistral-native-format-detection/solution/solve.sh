#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q '_MISTRAL_NATIVE_CONFIG_PATTERNS' python/sglang/srt/server_args.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/server_args.py b/python/sglang/srt/server_args.py
index 92e524a6be45..73dc2570ddfb 100644
--- a/python/sglang/srt/server_args.py
+++ b/python/sglang/srt/server_args.py
@@ -3159,22 +3159,42 @@ def _handle_load_format(self):
     def _is_mistral_native_format(self) -> bool:
         """Detect if the model uses Mistral native format (params.json + consolidated weights).

-        Models like Mistral-7B-Instruct-v0.3 have BOTH params.json (native) and
-        config.json (HF standard). When both exist, prefer the HF format to avoid
-        parameter name mismatches between consolidated.safetensors (native names
-        like layers.0.attention.wk.weight) and HuggingFace model classes (names
-        like model.layers.0.self_attn.k_proj.weight).
+        When both params.json and config.json exist, default to HF format to
+        avoid weight-name mismatches (e.g. Mistral-7B-Instruct-v0.3).
+
+        Exception: models routed through ``_load_mistral_large_3_for_causal_LM``
+        (mistral-large-3, mistral-small-4, leanstral) build their config from
+        params.json and expect native weight names, so native format is required
+        even when config.json is also present.
         """
+        # Keep in sync with the name checks in
+        # hf_transformers_utils.py::get_config / get_tokenizer.
+        _MISTRAL_NATIVE_CONFIG_PATTERNS = (
+            "mistral-large-3",
+            "mistral-small-4",
+            "leanstral",
+        )
+
+        def _check_format(has_params: bool, has_hf_config: bool) -> bool:
+            if has_params and not has_hf_config:
+                return True
+            if has_params and has_hf_config:
+                model_lower = str(self.model_path).lower()
+                if any(name in model_lower for name in _MISTRAL_NATIVE_CONFIG_PATTERNS):
+                    return True
+            return False
+
         if os.path.isdir(self.model_path):
             has_params = os.path.exists(os.path.join(self.model_path, "params.json"))
             has_hf_config = os.path.exists(os.path.join(self.model_path, "config.json"))
-            return has_params and not has_hf_config
+            return _check_format(has_params, has_hf_config)
+
         # For hub models, check remote files
         try:
             from huggingface_hub import HfApi

             files = {s.rfilename for s in HfApi().model_info(self.model_path).siblings}
-            return "params.json" in files and "config.json" not in files
+            return _check_format("params.json" in files, "config.json" in files)
         except Exception:
             return False

PATCH

echo "Patch applied successfully."
