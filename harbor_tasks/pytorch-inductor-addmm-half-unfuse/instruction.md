# Inductor: half-precision accuracy regression in addmm optimization

## Problem

In the PyTorch Inductor's post-grad FX passes, the `unfuse_bias_add_to_pointwise` pattern-matching optimization in `torch/_inductor/fx_passes/post_grad.py` splits fused `addmm` operations (matmul + bias add) into separate `mm` and pointwise `add` steps when a pointwise consumer (such as `gelu`) is detected. This enables further fusion opportunities in the scheduler.

However, for `bfloat16` and `float16` dtypes, this splitting introduces an extra precision truncation at the matmul output. With the fused `addmm`, cuBLAS keeps the matmul result in higher precision before combining with bias. When split into separate `mm` + `add`, the intermediate result is truncated to bf16/fp16 first. This per-layer RMSE difference compounds through deep models (e.g., Whisper's 8 attention layers), eventually exceeding accuracy thresholds.

## Observed Behavior

- When `bfloat16` or `float16` inputs go through the `unfuse_bias_add_to_pointwise` optimization, numerical results diverge from eager mode because the split introduces an extra truncation step
- The accuracy regression was observed on Whisper (openai/whisper-tiny) with bfloat16 on H100, exceeding the 3.0x RMSE accuracy threshold
- The issue was introduced by a change to the SDPA backend defaults that made this code path more common
- For `float32` and `float64` dtypes, no precision loss occurs and the optimization works correctly

## Expected Behavior

- The `unfuse_bias_add_to_pointwise` function in `torch/_inductor/fx_passes/post_grad.py` must skip the unfusing optimization for half-precision dtypes (`bfloat16` and `float16`), ensuring numerical results match eager mode
- The optimization must continue to apply for `float32` and `float64` inputs without any changes to their behavior
- Hint: the dtype of the input tensor is accessible via metadata on the `inp` argument