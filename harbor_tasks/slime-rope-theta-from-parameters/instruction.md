# Missing rope_theta resolution in DeepseekV32Bridge with transformers 5.x

## Problem

When using transformers 5.x, `DeepseekV32Bridge` in `slime_plugins/mbridge/deepseek_v32.py` fails during checkpoint conversion because `_build_config()` expects `hf_config.rope_theta` as a top-level attribute. However, transformers 5.x's `RotaryEmbeddingConfigMixin` moves `rope_theta` into the `rope_parameters` dictionary instead of keeping it as a direct attribute.

When accessing `hf_config.rope_theta`, an `AttributeError` is raised because the attribute does not exist on the config object.

## Expected Behavior

When `rope_theta` is not available as a top-level attribute on `hf_config`:
1. Resolve `rope_theta` from `hf_config.rope_parameters["rope_theta"]` if available
2. Use a default value of `1000000` when:
   - `rope_parameters` does not exist on the config
   - `rope_parameters` is `None`
   - `rope_parameters` is an empty dictionary
   - `rope_parameters["rope_theta"]` is not set

When `rope_theta` already exists as a top-level attribute on `hf_config` (transformers 4.x), the value must be preserved unchanged.

The following class members must be preserved and not removed:
- `_DSA_ATTENTION_MAPPING`
- `_weight_to_hf_format`
- `_weight_to_mcore_format`

The parent class initialization must still be invoked, with `hf_config` being passed through correctly.

## File to Modify

- `slime_plugins/mbridge/deepseek_v32.py`
