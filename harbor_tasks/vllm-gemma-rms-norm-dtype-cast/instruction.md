# GemmaRMSNorm produces incorrect output after IR ops refactor

## Problem

The `GemmaRMSNorm` layer produces numerically incorrect output. It was recently changed to delegate its forward pass to the generic `ir.ops.rms_norm` function, but this breaks Gemma's specific normalization pattern.

Gemma's RMS normalization has two key differences from standard RMSNorm (documented in the class docstring):
1. Uses `x * (1 + w)` instead of `x * w`
2. The dtype casting order matters: multiplication should happen in high precision before downcasting

The generic `ir.ops.rms_norm` in `vllm/ir/ops/layernorm.py` currently casts `x` to the weight's dtype before multiplying, then casts the result to the original dtype. This is backwards from what the standard RMSNorm contract requires (`x.to(orig_dtype) * w`), and prevents Gemma from using its own casting pattern.

Additionally, the kernel dispatch predicates in `vllm/kernels/vllm_c.py`, `vllm/kernels/aiter_ops.py`, and `vllm/kernels/xpu_ops.py` were made unnecessarily restrictive by requiring `weight.dtype == x.dtype`.

## Expected Behavior

- `GemmaRMSNorm` should have its own dedicated normalization implementation with proper Gemma-style dtype handling, rather than delegating to `ir.ops.rms_norm`
- `ir.ops.rms_norm` should cast `x` to the original dtype BEFORE weight multiplication, not after
- Kernel dispatch predicates should not check weight dtype matching
- `GemmaRMSNorm.forward_cuda` should use `torch.compile` for performance

## Files to Look At

- `vllm/model_executor/layers/layernorm.py` -- `GemmaRMSNorm` class, `forward_native`, `forward_cuda`
- `vllm/ir/ops/layernorm.py` -- generic `rms_norm` reference implementation
- `vllm/kernels/vllm_c.py` -- dispatch predicate `rms_no_var_size`
- `vllm/kernels/aiter_ops.py` -- dispatch predicate `rms_no_var_16bit_only`
- `vllm/kernels/xpu_ops.py` -- dispatch predicate `rms_no_var`
