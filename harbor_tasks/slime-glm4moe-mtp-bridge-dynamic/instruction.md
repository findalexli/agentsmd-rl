# GLM-4.7-Flash MTP Bridge: Stub Implementation Breaks Checkpoint Conversion

## Bug Description

The GLM-4.7-Flash (glm4_moe_lite) checkpoint bridge in `slime_plugins/mbridge/glm4moe_lite.py` is currently a stub — the `GLM4MoELiteBridge` class inherits from `DeepseekV3Bridge` but overrides nothing (`pass`). This causes three distinct failures when converting GLM-4.7-Flash checkpoints for MTP (Multi-Token Prediction) training:

### Issue 1: Hardcoded Layer Index

`DeepseekV3Bridge` hardcodes layer index **61** for MTP weight mappings in `_SHARED_STATE_DICT_MAPPING` and `_convert_mtp_param`. GLM-4.7-Flash has **47** hidden layers, so MTP parameter names like `model.layers.61.embed_tokens.weight` are wrong — they should reference layer 47. The bridge needs to dynamically determine the layer count from the model config's `num_hidden_layers` attribute.

### Issue 2: FP8 vs BF16 Weight Loading

`DeepseekV3Bridge._get_safetensor_io()` uses FP8 dequantization to load safetensors. GLM-4.7-Flash ships standard BF16 safetensors, so the FP8 path either fails or corrupts weights. The bridge should use the standard `SafeTensorIO` loader instead.

### Issue 3: Missing `rope_theta` Attribute

`DeepseekV3Bridge.__init__` (via `_build_config`) reads `hf_config.rope_theta` directly. GLM-4.7-Flash stores this value inside a `rope_parameters` dict (i.e., `hf_config.rope_parameters["rope_theta"]`). The bridge needs to extract and patch this before the parent's `__init__` runs.

### Separate Issue: Bridge Path Missing Critic Support

In `slime/backends/megatron_utils/model_provider.py`, the `bridge` megatron-to-hf conversion path (the `if args.megatron_to_hf_mode == "bridge"` branch around line 85) returns the provider directly without wrapping it for the critic role. The other code paths (custom model provider and the default model_provider function) both replace `model.output_layer` with a `LinearForLastLayer(output_size=1)` when `role == "critic"`, but the bridge path does not. This means critic models constructed via the bridge path get the wrong output layer.

## Relevant Files

- `slime_plugins/mbridge/glm4moe_lite.py` — the bridge class that needs implementation
- `slime/backends/megatron_utils/model_provider.py` — model provider function (bridge path)
