# Missing rope_theta resolution from rope_parameters dict in DeepseekV32Bridge

## Problem

`DeepseekV32Bridge` in `slime_plugins/mbridge/deepseek_v32.py` inherits from `DeepseekV3Bridge`, whose `_build_config()` method expects `hf_config.rope_theta` as a top-level attribute. However, in transformers 5.x, the `RotaryEmbeddingConfigMixin` moves `rope_theta` into the `rope_parameters` dictionary instead of keeping it as a direct attribute on the config object.

When using transformers 5.x, `hf_config.rope_theta` does not exist, causing an `AttributeError` when `_build_config()` tries to access it during checkpoint conversion.

The same fix pattern already exists in `GLM4MoELiteBridge` in `glm4moe_lite.py` -- an `__init__` method that resolves `rope_theta` from `rope_parameters` when the top-level attribute is not available.

## Expected Behavior

`DeepseekV32Bridge` should resolve `rope_theta` from the `rope_parameters` dict when the top-level attribute is not available (transformers 5.x), while remaining a no-op on transformers 4.x where `rope_theta` is set directly.

## File to Modify

- `slime_plugins/mbridge/deepseek_v32.py` -- add an `__init__` method to `DeepseekV32Bridge` that resolves `rope_theta`
