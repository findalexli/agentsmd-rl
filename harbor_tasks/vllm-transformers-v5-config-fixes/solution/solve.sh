#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency: check if already applied (look for _SPECULATIVE_DECODING_CONFIGS in config.py)
if grep -q '_SPECULATIVE_DECODING_CONFIGS' vllm/transformers_utils/config.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/transformers_utils/config.py b/vllm/transformers_utils/config.py
index 7836a44e73ea..d27134157293 100644
--- a/vllm/transformers_utils/config.py
+++ b/vllm/transformers_utils/config.py
@@ -119,6 +119,8 @@ def __getitem__(self, key):
     tarsier2="Tarsier2Config",
 )

+_SPECULATIVE_DECODING_CONFIGS: set[str] = {"eagle", "speculators"}
+
 _CONFIG_ATTRS_MAPPING: dict[str, str] = {
     "llm_config": "text_config",
 }
@@ -190,7 +192,7 @@ def parse(
                 dummy_model_type = hf_overrides(dummy_config).model_type
                 model_type = dummy_model_type.removeprefix("dummy_")

-        if model_type in _CONFIG_REGISTRY:
+        if model_type in _SPECULATIVE_DECODING_CONFIGS:
             config_class = _CONFIG_REGISTRY[model_type]
             config = config_class.from_pretrained(
                 model,
@@ -200,6 +202,14 @@ def parse(
                 **kwargs,
             )
         else:
+            if model_type in _CONFIG_REGISTRY:
+                # Register the config class to AutoConfig to ensure it's used in future
+                # calls to `from_pretrained`
+                config_class = _CONFIG_REGISTRY[model_type]
+                config_class.model_type = model_type
+                AutoConfig.register(model_type, config_class, exist_ok=True)
+                # Now that it is registered, it is not considered remote code anymore
+                trust_remote_code = False
             try:
                 kwargs = _maybe_update_auto_config_kwargs(kwargs, model_type=model_type)
                 config = AutoConfig.from_pretrained(
diff --git a/vllm/transformers_utils/configs/colmodernvbert.py b/vllm/transformers_utils/configs/colmodernvbert.py
index 97fad16bcf93..656980739689 100644
--- a/vllm/transformers_utils/configs/colmodernvbert.py
+++ b/vllm/transformers_utils/configs/colmodernvbert.py
@@ -20,7 +20,6 @@ def __init__(
         vlm_config: dict | None = None,
         **kwargs,
     ):
-        super().__init__(**kwargs)
         self.embedding_dim = embedding_dim

         if vlm_config is None:
@@ -55,6 +54,7 @@ def __init__(
             intermediate_size=vis_cfg.get("intermediate_size", 3072),
             num_attention_heads=vis_cfg.get("num_attention_heads", 12),
         )
+        super().__init__(**kwargs)

     @property
     def image_seq_len(self) -> int:
diff --git a/vllm/transformers_utils/configs/deepseek_vl2.py b/vllm/transformers_utils/configs/deepseek_vl2.py
index 9c816488c087..03f24319e287 100644
--- a/vllm/transformers_utils/configs/deepseek_vl2.py
+++ b/vllm/transformers_utils/configs/deepseek_vl2.py
@@ -87,6 +87,18 @@ def __init__(
         super().__init__(**kwargs)


+if hasattr(DeepseekV2Config, "validate"):
+    # Transformers v5
+    from huggingface_hub.dataclasses import strict
+
+    @strict
+    class DeepseekVLV2TextConfig(DeepseekV2Config):
+        kv_lora_rank: int | None = None
+else:
+    # Transformers v4
+    DeepseekVLV2TextConfig = DeepseekV2Config  # type: ignore[misc]
+
+
 class DeepseekVLV2Config(PretrainedConfig):
     model_type = "deepseek_vl_v2"
     architectures: list[str] | None = None
@@ -102,22 +114,17 @@ def __init__(
         candidate_resolutions: tuple[tuple[int, int]] = ((384, 384),),
         **kwargs,
     ):
-        super().__init__(**kwargs)
-
-        if self.architectures is None:
-            self.architectures = ["DeepseekVLV2ForCausalLM"]
+        if "architectures" not in kwargs:
+            kwargs["architectures"] = ["DeepseekVLV2ForCausalLM"]

-        vision_config = kwargs.get("vision_config", {})
+        vision_config = kwargs.pop("vision_config", {})
         self.vision_config = VisionEncoderConfig(**vision_config)

-        projector_config = kwargs.get("projector_config", {})
+        projector_config = kwargs.pop("projector_config", {})
         self.projector_config = MlpProjectorConfig(**projector_config)

-        language_config = kwargs.get("language_config", {})
-        # remove kv_lora_rank if not specified, passing None is prohibited
-        if language_config.get("kv_lora_rank") is None:
-            language_config.pop("kv_lora_rank", None)
-        self.text_config = DeepseekV2Config(**language_config)
+        language_config = kwargs.pop("language_config", {})
+        self.text_config = DeepseekVLV2TextConfig(**language_config)

         self.tile_tag = tile_tag
         self.global_view_pos = global_view_pos
@@ -125,7 +132,8 @@ def __init__(
         self.vocab_size = self.text_config.vocab_size

         # update model_type for OCR models
-        if "DeepseekOCRForCausalLM" in self.architectures:
+        if "DeepseekOCRForCausalLM" in kwargs["architectures"]:
             self.model_type = "deepseek_ocr"
-        elif "DeepseekOCR2ForCausalLM" in self.architectures:
+        elif "DeepseekOCR2ForCausalLM" in kwargs["architectures"]:
             self.model_type = "deepseek_ocr2"
+        super().__init__(**kwargs)
diff --git a/vllm/transformers_utils/configs/flex_olmo.py b/vllm/transformers_utils/configs/flex_olmo.py
index c343dc0999a8..d283fde3c00f 100644
--- a/vllm/transformers_utils/configs/flex_olmo.py
+++ b/vllm/transformers_utils/configs/flex_olmo.py
@@ -39,13 +39,6 @@ def __init__(
         if "architectures" not in kwargs:
             kwargs["architectures"] = ["FlexOlmoForCausalLM"]

-        super().__init__(
-            pad_token_id=pad_token_id,
-            bos_token_id=bos_token_id,
-            eos_token_id=eos_token_id,
-            tie_word_embeddings=tie_word_embeddings,
-            **kwargs,
-        )
         self.vocab_size = vocab_size
         self.max_position_embeddings = max_position_embeddings
         self.hidden_size = hidden_size
@@ -80,3 +73,10 @@ def __init__(
         # BC: if there is a 'type' field, move it to 'rope_type'.
         if self.rope_parameters is not None and "type" in self.rope_parameters:
             self.rope_parameters["rope_type"] = self.rope_parameters["type"]
+        super().__init__(
+            pad_token_id=pad_token_id,
+            bos_token_id=bos_token_id,
+            eos_token_id=eos_token_id,
+            tie_word_embeddings=tie_word_embeddings,
+            **kwargs,
+        )
diff --git a/vllm/transformers_utils/configs/isaac.py b/vllm/transformers_utils/configs/isaac.py
index ed36d19ebf66..c46667cb2ab1 100644
--- a/vllm/transformers_utils/configs/isaac.py
+++ b/vllm/transformers_utils/configs/isaac.py
@@ -50,8 +50,6 @@ def __init__(
         vision_attn_implementation: str | None = None,
         **kwargs,
     ):
-        super().__init__(**kwargs)
-
         if isinstance(text_config, dict):
             # from HF config
             self.text_config = self.sub_configs["text_config"](**text_config)
@@ -92,6 +90,7 @@ def __init__(
             vision_max_num_patches,
         )
         self.vision_attn_implementation = vision_attn_implementation
+        super().__init__(**kwargs)


 __all__ = [
diff --git a/vllm/transformers_utils/configs/qwen3_next.py b/vllm/transformers_utils/configs/qwen3_next.py
index a49a26378d2c..6a02476fbe1a 100644
--- a/vllm/transformers_utils/configs/qwen3_next.py
+++ b/vllm/transformers_utils/configs/qwen3_next.py
@@ -220,7 +220,6 @@ def __init__(
     ):
         if mlp_only_layers is None:
             mlp_only_layers = []
-        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
         self.vocab_size = vocab_size
         self.max_position_embeddings = max_position_embeddings
         self.hidden_size = hidden_size
@@ -279,6 +278,7 @@ def __init__(
         self.output_router_logits = output_router_logits
         self.router_aux_loss_coef = router_aux_loss_coef
         self.mlp_only_layers = mlp_only_layers
+        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)


 __all__ = ["Qwen3NextConfig"]
diff --git a/vllm/transformers_utils/configs/step3p5.py b/vllm/transformers_utils/configs/step3p5.py
index 435afd938212..d67b9dfff5f6 100644
--- a/vllm/transformers_utils/configs/step3p5.py
+++ b/vllm/transformers_utils/configs/step3p5.py
@@ -80,6 +80,9 @@ def __init__(

         self.att_impl_type = att_impl_type
         self.use_head_wise_attn_gate = use_head_wise_attn_gate
+        # For some reason the checkpoint has longer layer_types than num_hidden_layers
+        if layer_types is not None:
+            layer_types = layer_types[: self.num_hidden_layers]
         self.layer_types = layer_types
         self.use_rope_layers = use_rope_layers
         self.yarn_only_types = yarn_only_types

PATCH

echo "Patch applied successfully."
