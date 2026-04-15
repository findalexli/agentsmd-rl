# Inductor: half-precision accuracy regression in addmm optimization

## Problem

In the PyTorch Inductor's post-grad FX passes, a pattern-matching optimization splits fused `addmm` operations (matmul + bias add) into separate `mm` and pointwise `add` steps when a pointwise consumer (such as `gelu`) is detected. This enables further fusion opportunities in the scheduler.

However, for `bfloat16` and `float16` dtypes, this splitting introduces an extra precision truncation at the matmul output. With the fused `addmm`, cuBLAS keeps the matmul result in higher precision before combining with bias. When split into separate `mm` + `add`, the intermediate result is truncated to bf16/fp16 first. This per-layer RMSE difference compounds through deep models (e.g., Whisper's 8 attention layers), eventually exceeding accuracy thresholds.

## Observed Behavior

- Models using `addmm` with `bfloat16` and `float16` dtypes and pointwise consumers (e.g., `gelu(addmm(bias, x, w))`) produce different numerical results compared to eager mode
- The accuracy regression was observed on Whisper (openai/whisper-tiny) with bfloat16 on H100, exceeding the 3.0x RMSE accuracy threshold
- The issue was introduced by a change to the SDPA backend defaults that made this code path more common
- For `float32` and `float64` dtypes, no precision loss occurs and the optimization works correctly

## Expected Behavior

Fix the accuracy regression so that `bfloat16` and `float16` computations produce numerically correct results matching eager mode. The optimization should continue to function correctly for `float32` and `float64` dtypes without any change in behavior.
