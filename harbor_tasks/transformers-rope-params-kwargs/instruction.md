# Fix: RoPE parameters in kwargs not handled when config lacks rope_parameters attribute

## Problem

In the `PreTrainedConfig.__post_init__` method in `src/transformers/configuration_utils.py`, when a model config receives `rope_scaling` and `rope_theta` as kwargs (e.g., from a saved config JSON), the RoPE parameter conversion (`convert_rope_params_to_dict`) is only called if the config class has a `rope_parameters` attribute. If a config class does not define `rope_parameters` as a class attribute but receives these RoPE keys through kwargs, they are silently ignored and end up being set as arbitrary attributes via the generic `setattr` loop at the end of `__post_init__`.

After config validation was tightened to run after initialization, configs that rely on legacy-format RoPE keys in kwargs (like `rope_scaling` and `rope_theta`) now fail validation because these keys are never converted to the standardized `rope_parameters` dict format.

## Root Cause

The `__post_init__` method only checks `if hasattr(self, "rope_parameters")` before calling `convert_rope_params_to_dict`. There is no fallback branch for configs that receive `rope_scaling` and `rope_theta` through kwargs without having defined `rope_parameters` as a dataclass field. The conversion method is never called for these configs, leaving the RoPE parameters in their legacy format.

## Expected Fix

When a config does not have a `rope_parameters` attribute but kwargs contain both `rope_scaling` and `rope_theta`, the code should still call `convert_rope_params_to_dict` to handle the legacy format. A deprecation warning should be emitted to inform users about the need to update their config to use `rope_parameters`.

## File to Modify

- `src/transformers/configuration_utils.py` -- the `__post_init__` method of `PreTrainedConfig`
