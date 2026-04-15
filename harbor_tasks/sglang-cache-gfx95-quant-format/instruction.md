# Cache gfx95 quant format detection in DeepseekV2DecoderLayer

## Problem

The `DeepseekV2DecoderLayer.forward()` method in `python/sglang/srt/models/deepseek_v2.py` recomputes quant_format detection logic on every forward call. This is wasteful because the value depends only on static properties that never change between calls:

1. Whether gfx95 is supported (via the module-level `_is_gfx95_supported` flag)
2. The existence and dtype of `self_attn.fused_qkv_a_proj_with_mqa.weight`

The current inline logic in `forward()` evaluates a complex nested conditional to determine one of three quant_format values:

- `"mxfp4"` when the weight dtype is `torch.uint8`
- `"fp8"` when the weight dtype is `torch.float8_e4m3fn`
- `""` (empty string) otherwise (including when gfx95 is not supported or weight is absent)

This entire conditional block runs on every forward pass even though the result is always the same for a given model instance.

## Expected Behavior

The quant_format detection should be computed once during initialization rather than on every forward call. The fix should:

1. Factor the detection logic out of `forward()` into a dedicated method on `DeepseekV2DecoderLayer` with a `str` return type annotation
2. Store the computed result as a cached instance attribute during `__init__`
3. Replace the inline computation in `forward()` with the cached value

The detection method must contain real logic (not a stub) that checks for gfx95 support and handles the `torch.uint8` → `"mxfp4"` and `torch.float8_e4m3fn` → `"fp8"` cases, returning `""` as the fallback.

## Files

- `python/sglang/srt/models/deepseek_v2.py` — Contains the `DeepseekV2DecoderLayer` class with the relevant `forward()` and `__init__` methods

## Reference

This refactoring corresponds to PR #22143 in sgl-project/sglang. The PR can be fetched from the cloned repository to see the exact naming and implementation details used.
