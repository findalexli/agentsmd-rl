# Cache gfx95 quant format detection in DeepseekV2DecoderLayer

## Problem

The `DeepseekV2DecoderLayer.forward()` method currently recomputes the `quant_format` detection logic on every forward call. This is inefficient because:

1. The `quant_format` value depends only on static properties (weight dtype of `fused_qkv_a_proj_with_mqa`)
2. The same nested conditional logic runs repeatedly during inference
3. On non-gfx95 platforms, this check is unnecessary overhead

The current code in `forward()` has a complex nested conditional that checks `_is_gfx95_supported`, the existence of `fused_qkv_a_proj_with_mqa`, its `weight` attribute, and the dtype to determine whether to use "mxfp4", "fp8", or "" (empty string).

## Expected Behavior

1. Extract the `quant_format` detection logic into a dedicated `_detect_gfx95_quant_format()` method on `DeepseekV2DecoderLayer`
2. Cache the result in `__init__` as `self._gfx95_quant_format` so it's computed once instead of on every forward call
3. On non-gfx95 platforms, the value should be empty string immediately with zero runtime overhead
4. On gfx95 platforms, it should be lazily computed (though in the patch, it's computed in `__init__`)
5. The `forward()` method should use the cached `self._gfx95_quant_format` value instead of recomputing

## Files to Look At

- `python/sglang/srt/models/deepseek_v2.py` — Contains the `DeepseekV2DecoderLayer` class that needs modification
  - Look at the `forward()` method for the current inline `quant_format` logic
  - Look at `__init__` to add the caching

## Notes

- The method should return a string: "mxfp4" for uint8 weights, "fp8" for float8_e4m3fn weights, or "" otherwise
- The `_is_gfx95_supported` variable is already defined in the module scope (imported from deepseek_common.utils)
- The fix should preserve all existing behavior while improving performance by caching
