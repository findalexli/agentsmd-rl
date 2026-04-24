# GLM-4.7-Flash MTP checkpoint bridge is non-functional

## Problem

The `GLM4MoELiteBridge` class in `slime_plugins/mbridge/glm4moe_lite.py` is a stub — it inherits from `DeepseekV3Bridge` but doesn't override any behavior. When using MTP (Multi-Token Prediction) training with GLM-4.7-Flash, several assumptions the parent bridge makes about the model don't hold:

1. **rope_theta lookup fails**: GLM-4.7-Flash stores `rope_theta` inside a `rope_parameters` dict rather than as a top-level config attribute. The parent bridge's `_build_config()` accesses `hf_config.rope_theta` directly, which doesn't exist for this model.

2. **MTP weight name conversion uses wrong layer index**: DeepSeek V3 has 61 transformer layers and the parent bridge uses `model.layers.61` in MTP weight mappings. GLM-4.7-Flash has 47 layers, so MTP checkpoint conversion produces weight names that reference non-existent layer 61 instead of the correct layer index.

3. **Wrong safetensor I/O class**: The parent bridge's `_get_safetensor_io` returns an FP8 dequantization variant. GLM-4.7-Flash ships standard bf16 safetensors.

4. **Shared weight mapping uses hardcoded layer index**: The parent's `_SHARED_STATE_DICT_MAPPING` hardcodes layer 61 for embedding and output layer mappings. GLM-4.7-Flash needs these mapped to the correct dynamic layer index derived from the model's actual layer count.

5. **MTP parameter name conversion incomplete**: The bridge needs to convert MCore-format MTP parameter names to HuggingFace format. Direct MTP layer parameters (enorm, hnorm, eh_proj, final_layernorm) need mapping, and transformer-layer parameters within the MTP layer need delegation to the parent's attention/MLP weight mapping methods.

6. **Shared weight export incomplete**: When converting weights to HF format, shared weights (embedding and output) should produce entries for both the base model name and the MTP layer name.

## Files to Look At

- `slime_plugins/mbridge/glm4moe_lite.py` — The GLM-4.7-Flash checkpoint bridge (currently a stub)
- `slime/backends/megatron_utils/model_provider.py` — Model provider that configures Megatron model initialization

## Expected Behavior

After the fix, the bridge should correctly handle GLM-4.7-Flash models:
- rope_theta is read from the nested rope_parameters dict when present, and defaults to 1000000 when absent
- All MTP weight name mappings use the dynamic layer index from the model's num_hidden_layers (47 for GLM-4.7-Flash)
- Safetensor loading uses the standard SafeTensorIO class, not FP8 dequantization
- Shared weight mappings are computed dynamically using the model's actual layer count
- MTP parameter names are converted correctly with the dynamic layer index

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `black (Python formatter)`
