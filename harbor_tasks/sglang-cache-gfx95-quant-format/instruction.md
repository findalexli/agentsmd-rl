# Redundant quant format computation in DeepseekV2DecoderLayer

## Problem

In the `sglang` repository, the `DeepseekV2DecoderLayer` class in `python/sglang/srt/models/deepseek_v2.py` has a performance issue: its `forward()` method recomputes a quant format string on every call. This value depends only on static properties of the model instance — hardware support flags and weight dtypes — that never change after the layer is constructed.

The detection logic determines one of three format strings based on the dtype of an attention weight:

| Weight dtype | Quant format |
|---|---|
| `torch.uint8` | `"mxfp4"` |
| `torch.float8_e4m3fn` | `"fp8"` |
| anything else | `""` |

Because the result is constant for any given model instance, recomputing this nested conditional on every forward pass is wasteful.

## Task

Fix the performance issue so that the quant format value is determined once during layer construction and reused on subsequent forward calls, rather than being recalculated inline every time `forward()` is invoked. The detection logic must correctly handle all three dtype cases listed above.

## Constraints

- Only modify `python/sglang/srt/models/deepseek_v2.py`.
- The `DeepseekV2DecoderLayer` class must retain its `__init__` and `forward` methods.
- The modified code must pass `ruff`, `black`, `isort`, and `codespell` checks.
