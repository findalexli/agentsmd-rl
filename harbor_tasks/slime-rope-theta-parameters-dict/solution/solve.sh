#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

if grep -q "rope_parameters" slime/backends/megatron_utils/arguments.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/arguments.py b/slime/backends/megatron_utils/arguments.py
index d724b899c..68a7aad71 100644
--- a/slime/backends/megatron_utils/arguments.py
+++ b/slime/backends/megatron_utils/arguments.py
@@ -40,6 +40,15 @@ def equal(x, y):
     if hasattr(hf_config, "text_config"):
         hf_config = hf_config.text_config
 
+    # Some models store rope_theta inside rope_parameters dict rather than
+    # as a top-level attribute.  Prefer the dict value when available so
+    # the validation doesn't compare against a stale class default.
+    rope_params = getattr(hf_config, "rope_parameters", None)
+    if isinstance(rope_params, dict) and "rope_theta" in rope_params:
+        _hf_rope_theta = rope_params["rope_theta"]
+    else:
+        _hf_rope_theta = getattr(hf_config, "rope_theta", None)
+
     for hf_config_name, megatron_config_name, compare_fn in [
         ("hidden_size", "hidden_size", equal),
         ("num_attention_heads", "num_attention_heads", equal),
@@ -47,7 +56,6 @@ def equal(x, y):
         ("intermediate_size", "ffn_hidden_size", equal),
         ("tie_word_embeddings", "untie_embeddings_and_output_weights", lambda x, y: not x == y),
         ("rms_norm_eps", "norm_epsilon", equal),
-        ("rope_theta", "rotary_base", equal),
     ]:
         if hasattr(hf_config, hf_config_name):
             if not compare_fn(getattr(hf_config, hf_config_name), getattr(args, megatron_config_name)):
@@ -56,6 +64,14 @@ def equal(x, y):
                     f"{megatron_config_name} {getattr(args, megatron_config_name)}, please check the config."
                 )
 
+    # Validate rope_theta separately using the resolved value
+    if _hf_rope_theta is not None:
+        if not equal(_hf_rope_theta, getattr(args, "rotary_base", None)):
+            errors.append(
+                f"rope_theta in hf config {_hf_rope_theta} is not equal to "
+                f"rotary_base {getattr(args, 'rotary_base', None)}, please check the config."
+            )
+
     if len(errors) > 0:
         raise AssertionError("hf_validate_args failed: " + "; ".join(errors))
PATCH
