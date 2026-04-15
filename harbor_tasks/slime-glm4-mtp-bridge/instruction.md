# GLM-4.7-Flash MTP checkpoint bridge is non-functional

## Problem

The `GLM4MoELiteBridge` class in `slime_plugins/mbridge/glm4moe_lite.py` is a stub — it inherits from `DeepseekV3Bridge` but doesn't override any behavior. This causes multiple failures when trying to use MTP (Multi-Token Prediction) training with GLM-4.7-Flash:

1. **rope_theta lookup fails**: GLM-4.7-Flash stores `rope_theta` inside a `rope_parameters` dict rather than as a top-level config attribute. The parent bridge's `_build_config()` accesses `hf_config.rope_theta` directly, which doesn't exist for this model. When `rope_parameters` is absent entirely, `rope_theta` should default to `1000000`.

2. **Wrong layer index for MTP weights**: DeepSeek V3 has 61 transformer layers and the parent bridge hardcodes `model.layers.61` for MTP weight mapping. GLM-4.7-Flash has `num_hidden_layers=47`, so MTP checkpoint conversion produces incorrect weight names (layer 61 instead of 47). The bridge should use `num_hidden_layers` as the dynamic layer index `{n}` throughout all MTP weight name mappings.

3. **FP8 dequantization applied incorrectly**: The parent bridge's `_get_safetensor_io` returns an FP8 dequantization variant. GLM-4.7-Flash ships standard bf16 safetensors, so the bridge should use the standard `SafeTensorIO` class from `mbridge.core.safetensor_io` instead.

4. **Shared weight mapping broken**: The `_SHARED_STATE_DICT_MAPPING` in the parent hardcodes layer 61. For a model with `num_hidden_layers={n}`, the mapping needs to include:
   - `embedding.word_embeddings.weight` → [`model.embed_tokens.weight`, `model.layers.{n}.embed_tokens.weight`]
   - `output_layer.weight` → [`lm_head.weight`, `model.layers.{n}.shared_head.head.weight`]

5. **MTP parameter name conversion missing**: The bridge's MTP parameter conversion (`_convert_mtp_param`) needs to map MCore-format MTP layer parameter names to HuggingFace format using the dynamic layer index `{n}`. The following direct mappings are required:
   - `mtp.layers.0.enorm.weight` → `model.layers.{n}.enorm.weight`
   - `mtp.layers.0.hnorm.weight` → `model.layers.{n}.hnorm.weight`
   - `mtp.layers.0.eh_proj.weight` → `model.layers.{n}.eh_proj.weight`
   - `mtp.layers.0.final_layernorm.weight` → `model.layers.{n}.shared_head.norm.weight`

   Transformer-layer parameters within the MTP layer should be delegated through the parent class's existing attention/MLP weight name mapping methods. For example:
   - `mtp.layers.0.transformer_layer.self_attention.linear_proj.weight` → `model.layers.{n}.self_attn.o_proj.weight`
   - `mtp.layers.0.transformer_layer.mlp.linear_fc2.weight` → `model.layers.{n}.mlp.down_proj.weight`

6. **Shared weight export**: When converting weights to HF format via `_weight_to_hf_format`, shared weights (embedding and output) should produce entries for both the base model name and the MTP layer name. For example, `embedding.word_embeddings.weight` should produce both `model.embed_tokens.weight` and `model.layers.{n}.embed_tokens.weight`, and `output_layer.weight` should produce both `lm_head.weight` and `model.layers.{n}.shared_head.head.weight`.

## Files to Look At

- `slime_plugins/mbridge/glm4moe_lite.py` — The GLM-4.7-Flash checkpoint bridge (currently a stub)
- `slime/backends/megatron_utils/model_provider.py` — Model provider that configures Megatron model initialization
