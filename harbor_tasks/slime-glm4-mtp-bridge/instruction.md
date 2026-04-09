# GLM-4.7-Flash MTP checkpoint bridge is non-functional

## Problem

The `GLM4MoELiteBridge` class in `slime_plugins/mbridge/glm4moe_lite.py` is a stub — it inherits from `DeepseekV3Bridge` but doesn't override any behavior. This causes multiple failures when trying to use MTP (Multi-Token Prediction) training with GLM-4.7-Flash:

1. **rope_theta lookup fails**: GLM-4.7-Flash stores `rope_theta` inside a `rope_parameters` dict rather than as a top-level config attribute. The parent bridge's `_build_config()` accesses `hf_config.rope_theta` directly, which doesn't exist for this model.

2. **Wrong layer index for MTP weights**: DeepSeek V3 has 61 transformer layers and the parent bridge hardcodes `model.layers.61` for MTP weight mapping. GLM-4.7-Flash has 47 layers, so MTP checkpoint conversion produces incorrect weight names (layer 61 instead of layer 47).

3. **FP8 dequantization applied incorrectly**: The parent bridge's `_get_safetensor_io` uses FP8 dequantization (via triton kernels), but GLM-4.7-Flash ships standard bf16 safetensors. This causes import failures on systems without triton/CUDA and incorrect weight loading otherwise.

4. **Shared weight mapping broken**: The `_weight_to_hf_format` method in the parent checks `self.config.num_layers == 61` before handling shared embedding/output weights for MTP. For a 47-layer model, this condition is never true, so shared weights are not duplicated to the MTP layer.

## Expected Behavior

`GLM4MoELiteBridge` should properly adapt the DeepSeek V3 bridge for GLM-4.7-Flash by:
- Extracting `rope_theta` from `rope_parameters` when it's not a direct attribute
- Using the model's actual `num_hidden_layers` for MTP weight indexing instead of hardcoded 61
- Using standard `SafeTensorIO` for bf16 safetensors
- Handling shared embedding/output weights with the dynamic layer count

## Files to Look At

- `slime_plugins/mbridge/glm4moe_lite.py` — The GLM-4.7-Flash checkpoint bridge (currently a stub)
- `slime/backends/megatron_utils/model_provider.py` — Model provider that configures Megatron model initialization
