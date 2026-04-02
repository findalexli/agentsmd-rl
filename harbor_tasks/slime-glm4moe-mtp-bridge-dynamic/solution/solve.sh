#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency: check if fix is already applied
if grep -q '_get_safetensor_io' slime_plugins/mbridge/glm4moe_lite.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/model_provider.py b/slime/backends/megatron_utils/model_provider.py
index 31db8b0da8..bd5f711288 100644
--- a/slime/backends/megatron_utils/model_provider.py
+++ b/slime/backends/megatron_utils/model_provider.py
@@ -96,6 +96,20 @@ def wrapped_model_provider(
         if getattr(args, "decoder_last_pipeline_num_layers", None) is not None:
             provider.num_layers_in_last_pipeline_stage = args.decoder_last_pipeline_num_layers
         provider.finalize()
+
+        if role == "critic":
+            _original_provide = provider.provide
+
+            def _critic_provide(pre_process=True, post_process=True, vp_stage=None):
+                model = _original_provide(pre_process=pre_process, post_process=post_process, vp_stage=vp_stage)
+                if post_process:
+                    model.output_layer = LinearForLastLayer(
+                        input_size=model.config.hidden_size, output_size=1, config=model.config
+                    )
+                return model
+
+            return _critic_provide
+
         return provider.provide

     def model_provider(pre_process: bool = True, post_process: bool = True, vp_stage: int | None = None) -> GPTModel:
diff --git a/slime_plugins/mbridge/glm4moe_lite.py b/slime_plugins/mbridge/glm4moe_lite.py
index 8306d281ae..ceaa8d86e0 100644
--- a/slime_plugins/mbridge/glm4moe_lite.py
+++ b/slime_plugins/mbridge/glm4moe_lite.py
@@ -1,7 +1,76 @@
+import torch
 from mbridge.core import register_model
+from mbridge.core.safetensor_io import SafeTensorIO
 from mbridge.models import DeepseekV3Bridge


 @register_model("glm4_moe_lite")
 class GLM4MoELiteBridge(DeepseekV3Bridge):
-    pass
+    """
+    Bridge for GLM-4.7-Flash (glm4_moe_lite) models.
+
+    Extends DeepseekV3Bridge with:
+    - Dynamic MTP layer indexing (parent hardcodes layer 61 for DeepSeek V3)
+    - Standard bf16 safetensor loading (parent uses FP8 dequant for DeepSeek V3)
+    """
+
+    def __init__(self, hf_config, **kwargs):
+        # Patch rope_theta: GLM-4.7-Flash stores it in rope_parameters dict,
+        # but DeepseekV3Bridge._build_config() expects hf_config.rope_theta directly.
+        if not hasattr(hf_config, "rope_theta"):
+            rope_params = getattr(hf_config, "rope_parameters", None) or {}
+            hf_config.rope_theta = rope_params.get("rope_theta", 1000000)
+        super().__init__(hf_config, **kwargs)
+        # Override the shared state dict mapping with dynamic layer index.
+        # DeepseekV3Bridge hardcodes layer 61; GLM-4.7-Flash uses num_hidden_layers (47).
+        n = hf_config.num_hidden_layers
+        if getattr(hf_config, "num_nextn_predict_layers", 0) and n:
+            self._SHARED_STATE_DICT_MAPPING = {
+                "embedding.word_embeddings.weight": [
+                    "model.embed_tokens.weight",
+                    f"model.layers.{n}.embed_tokens.weight",
+                ],
+                "output_layer.weight": [
+                    "lm_head.weight",
+                    f"model.layers.{n}.shared_head.head.weight",
+                ],
+            }
+
+    def _get_safetensor_io(self, weights_path: str):
+        """Use standard SafeTensorIO — GLM-4.7-Flash ships bf16 safetensors, not FP8."""
+        return SafeTensorIO(self._get_actual_hf_path(weights_path))
+
+    def _weight_to_hf_format(
+        self, mcore_weights_name: str, mcore_weights: torch.Tensor
+    ) -> tuple[list[str], list[torch.Tensor]]:
+        """Handle shared embedding/output weights for MTP with dynamic layer count."""
+        if (
+            self.config.mtp_num_layers is not None
+            and self.config.mtp_num_layers >= 1
+            and mcore_weights_name in self._SHARED_STATE_DICT_MAPPING
+        ):
+            hf_names = self._SHARED_STATE_DICT_MAPPING[mcore_weights_name]
+            return hf_names, [mcore_weights] * len(hf_names)
+        # Skip DeepseekV3Bridge's _weight_to_hf_format (hardcoded 61) and go to Bridge base
+        return super(DeepseekV3Bridge, self)._weight_to_hf_format(mcore_weights_name, mcore_weights)
+
+    def _convert_mtp_param(self, name: str) -> list[str]:
+        """Convert MTP parameter names with dynamic layer count (not hardcoded 61)."""
+        assert self.config.mtp_num_layers == 1, "only support one mtp layer for now"
+        n = self.config.num_layers
+        direct_name_mapping = {
+            "mtp.layers.0.enorm.weight": f"model.layers.{n}.enorm.weight",
+            "mtp.layers.0.hnorm.weight": f"model.layers.{n}.hnorm.weight",
+            "mtp.layers.0.eh_proj.weight": f"model.layers.{n}.eh_proj.weight",
+            "mtp.layers.0.final_layernorm.weight": f"model.layers.{n}.shared_head.norm.weight",
+        }
+        if name in direct_name_mapping:
+            return [direct_name_mapping[name]]
+        assert "mtp.layers.0.transformer_layer" in name, f"mtp not found in {name}"
+        proxy_name = name.replace("mtp.layers.0.transformer_layer", f"decoder.layers.{n}")
+        if "self_attention" in proxy_name or "input_layernorm.weight" in proxy_name:
+            return self._weight_name_mapping_attention(proxy_name)
+        elif "mlp" in proxy_name:
+            return self._weight_name_mapping_mlp(proxy_name)
+        else:
+            raise NotImplementedError(f"Unsupported MTP parameter name: {name}")

PATCH

echo "Patch applied successfully."
