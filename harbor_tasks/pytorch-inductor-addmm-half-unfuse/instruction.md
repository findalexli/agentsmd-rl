# Inductor: addmm unfused for half-precision dtypes causes accuracy regression

## Problem

The Inductor pattern matcher has an optimization pass (`unfuse_bias_add_to_pointwise` in `torch/_inductor/fx_passes/post_grad.py`) that splits fused `addmm` operations into separate `mm` + pointwise `add` when a pointwise consumer is present. This enables further fusion opportunities in the Inductor scheduler.

However, this unfusing introduces an extra precision truncation at the `mm` output for `bfloat16` and `float16` dtypes. With the fused `addmm`, cuBLAS keeps the matmul result in higher precision before combining with bias. When unfused into `mm` + `add`, the intermediate result is truncated to bf16/fp16 first. This per-layer RMSE difference compounds through deep models (e.g., Whisper's 8 attention layers), eventually exceeding accuracy thresholds.

## Observed Behavior

- Models using `addmm` with half-precision dtypes and pointwise consumers (e.g., `gelu(addmm(bias, x, w))`) produce different numerical results compared to eager mode
- The accuracy regression was observed on Whisper (openai/whisper-tiny) with bfloat16 on H100, exceeding the 3.0x RMSE accuracy threshold
- The issue was introduced by a change to the SDPA backend defaults that made this code path more common

## Expected Behavior

The `unfuse_bias_add_to_pointwise` pass should not unfuse `addmm` operations when the inputs are `bfloat16` or `float16`, since the precision loss from the extra truncation outweighs the fusion benefit.

## Relevant Files

- `torch/_inductor/fx_passes/post_grad.py` — the `unfuse_bias_add_to_pointwise` function
