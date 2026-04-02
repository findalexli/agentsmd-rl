# FP8Experts class does not support static activation quantization

## Problem

The `FP8Experts` class in `src/transformers/integrations/finegrained_fp8.py` currently hard-codes an assertion that only `"dynamic"` activation quantization is supported. When loading FP8-quantized Mixture-of-Experts models with static activation scales (e.g., pre-computed per-expert activation scales), the class raises an `AssertionError` at construction time.

This means models quantized with `activation_scheme="static"` in their quantization config cannot be loaded through the standard `FbgemmFp8Config` path.

## Expected behavior

`FP8Experts` should:
1. Accept `activation_scheme="static"` without crashing
2. Register per-expert activation scale parameters for both the gate/up projection and the down projection
3. Use those static scales during the forward pass to quantize activations, instead of dynamically computing scales via the Triton kernel at runtime

## Additional context

The `linear` method in `FP8Experts` currently always calls the Triton kernel's `fp8_act_quant` to dynamically quantize activations. For the static path, it should instead use the pre-registered activation scale to manually quantize: divide the input by the scale, clamp to the FP8 range, and cast to FP8 dtype.

Additionally, the multi-GPU code paths (`w8a8_fp8_matmul`, `fp8_batched_mm_experts_forward`, `fp8_grouped_mm_experts_forward`) do not set the CUDA device context before Triton JIT compilation. This causes Triton to compile/launch kernels on the wrong GPU when tensors reside on a device different from the active CUDA context.

## Files to investigate

- `src/transformers/integrations/finegrained_fp8.py` — the `FP8Experts` class, `linear` method, `forward` method, and the module-level `w8a8_fp8_matmul` function
