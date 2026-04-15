# Cache gfx95 quant format detection in DeepseekV2DecoderLayer

## Problem

The `DeepseekV2DecoderLayer.forward()` method in `python/sglang/srt/models/deepseek_v2.py` recomputes quant_format detection logic on every forward call. This is wasteful because the value depends only on static properties that never change between calls:

- Whether gfx95 is supported (via the module-level `_is_gfx95_supported` flag)
- The existence and dtype of `self_attn.fused_qkv_a_proj_with_mqa.weight`
- The weight dtype is one of `torch.uint8`, `torch.float8_e4m3fn`, or something else

The current inline logic evaluates a nested conditional to determine one of three values:

- `"mxfp4"` when the weight dtype is `torch.uint8`
- `"fp8"` when the weight dtype is `torch.float8_e4m3fn`
- `""` (empty string) otherwise

This conditional block runs on every forward pass even though the result is constant for a given model instance.

## Expected Behavior

The quant_format value is recomputed identically on every forward call. It should instead be computed once and reused. Specifically:

1. The detection logic should be a named method on `DeepseekV2DecoderLayer` with a `str` return type annotation
2. The result should be stored as an instance attribute in `__init__`
3. `forward()` should reference the stored value instead of recomputing it

The detection method must contain real logic (not a stub) that handles the dtype cases described above.

## Files

- `python/sglang/srt/models/deepseek_v2.py` — Contains the `DeepseekV2DecoderLayer` class with `forward()` and `__init__` methods

## What to Look For

The tests check that:

- `DeepseekV2DecoderLayer` has a method that returns `str` and is called from `__init__` to populate an attribute
- `forward()` uses the cached attribute rather than inline computation
- The detection method body contains checks for `torch.uint8`, `float8_e4m3fn`, `mxfp4`, and `fp8`
