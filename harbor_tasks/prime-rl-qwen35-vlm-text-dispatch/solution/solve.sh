#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'def is_vlm_architecture' src/prime_rl/utils/vlm.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/trainer/model.py b/src/prime_rl/trainer/model.py
index 1dad99a751..b1d8b530c2 100644
--- a/src/prime_rl/trainer/model.py
+++ b/src/prime_rl/trainer/model.py
@@ -41,7 +41,7 @@
 )
 from prime_rl.trainer.world import get_world
 from prime_rl.utils.logger import get_logger
-from prime_rl.utils.vlm import get_language_model, get_vision_encoder
+from prime_rl.utils.vlm import get_language_model, get_vision_encoder, is_vlm_architecture


 def _patch_qwen3_5_moe_conversion_mapping():
@@ -193,8 +193,7 @@ def get_model(
         f"Loading model config (name={config.name}, attn={config.attn}, trust_remote_code={config.trust_remote_code})"
     )

-    # VLM mode is enabled by setting [model.vlm] in config
-    is_vlm = config.vlm is not None
+    is_vlm_training = config.vlm is not None

     if "Qwen3.5" in config.name or "qwen3_5" in config.name.lower():
         _patch_qwen3_5_text_position_ids()
@@ -207,8 +206,9 @@ def get_model(
         ),
     )
     model_config.use_cache = False
+    is_vlm_arch = is_vlm_architecture(model_config)

-    if is_vlm:
+    if is_vlm_training:
         logger.info(f"Detected vision-language model: {config.name}")
         if config.optimization_dtype != "bfloat16" or config.reduce_dtype != "bfloat16":
             raise ValueError(
@@ -261,9 +261,9 @@ def get_model(
         target_config.num_hidden_layers = num_hidden_layers

     # Determine the implementation to use
-    custom_vlm_cls = get_custom_vlm_cls(model_config) if is_vlm else None
+    custom_vlm_cls = get_custom_vlm_cls(model_config) if is_vlm_arch else None
     if config.impl == "auto":
-        if is_vlm:
+        if is_vlm_arch:
             impl_to_use = "custom" if custom_vlm_cls is not None else "hf"
         else:
             impl_to_use = "custom" if supports_custom_impl(model_config) else "hf"
@@ -272,13 +272,12 @@ def get_model(
         impl_to_use = config.impl

     with device:
-        if is_vlm:
-            if impl_to_use == "custom" and custom_vlm_cls is not None:
-                model_cls = custom_vlm_cls
-            else:
-                from transformers import AutoModelForImageTextToText
+        if impl_to_use == "custom" and custom_vlm_cls is not None:
+            model_cls = custom_vlm_cls
+        elif is_vlm_arch:
+            from transformers import AutoModelForImageTextToText

-                model_cls = AutoModelForImageTextToText
+            model_cls = AutoModelForImageTextToText
         else:
             match impl_to_use:
                 case "hf":
@@ -288,7 +287,7 @@ def get_model(

         load_model_start_time = time.perf_counter()
         # HF VLM models require torch_dtype; custom PrimeRL models and text Auto models use dtype
-        use_torch_dtype = is_vlm and model_cls is not custom_vlm_cls
+        use_torch_dtype = is_vlm_arch and model_cls is not custom_vlm_cls
         dtype_kwarg = {"torch_dtype": dtype} if use_torch_dtype else {"dtype": dtype}
         if device == torch.device("meta"):
             logger.info(f"Loading model {config.name} using {model_cls.__name__} to meta device")
@@ -303,8 +302,8 @@ def get_model(
             )
         logger.debug(f"Loaded model {config.name} in {time.perf_counter() - load_model_start_time:.2f} seconds")

-    # For VLM models, freeze the vision encoder
-    if is_vlm:
+    # For VLM training, freeze the vision encoder
+    if is_vlm_training:
         freeze_vision_encoder(model, override_attr=config.vlm.vision_encoder_attr)

     assert model.lm_head.weight.dtype == dtype, (
@@ -343,15 +342,15 @@ def setup_fsdp(model: nn.Module, config: ModelConfig, parallel_dims: ParallelDim

         dp_mod_ep_mesh = parallel_dims.world_mesh[tuple(dp_mod_ep_mesh_dim_names)]

-    is_vlm = config.vlm is not None
-    if is_vlm:
+    is_vlm_training = config.vlm is not None
+    if is_vlm_training:
         vision_encoder = get_vision_encoder(model, override=config.vlm.vision_encoder_attr)
         if vision_encoder is None:
             raise ValueError(f"VLM model {config.name} has no recognized vision encoder")
         fully_shard(vision_encoder, mesh=hsdp_mesh, **fsdp_config)
         get_logger().info("Applied FSDP to frozen vision encoder")

-    language_model = get_language_model(model, override=config.vlm.language_model_attr if is_vlm else None)
+    language_model = get_language_model(model, override=config.vlm.language_model_attr if is_vlm_training else None)
     transformer_layers = language_model.layers

     for transformer_block in transformer_layers:
diff --git a/src/prime_rl/utils/vlm.py b/src/prime_rl/utils/vlm.py
index 7a51490d5e..15b5f1bf3b 100644
--- a/src/prime_rl/utils/vlm.py
+++ b/src/prime_rl/utils/vlm.py
@@ -80,6 +80,11 @@ def get_language_model(model: nn.Module, override: str | None = None) -> nn.Modu
     return model.model


+def is_vlm_architecture(model_config: PretrainedConfig) -> bool:
+    """Check if the model config belongs to a known VLM architecture."""
+    return _get_model_info_from_config(model_config) is not None
+
+
 def get_layer_prefix(model_config: PretrainedConfig, override: str | None = None) -> str:
     """Return the weight key prefix for language model layers.

PATCH

echo "Patch applied successfully."
