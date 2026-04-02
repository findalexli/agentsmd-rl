# Conch kernel crashes on 3D tensor input

## Bug

When running quantized models through the transformers backend, the conch quantization kernel crashes with:

```
ValueError: too many values to unpack (expected 2)
```

The error occurs in the `apply_weights` method of `ConchLinearKernel` in `vllm/model_executor/kernels/linear/mixed_precision/conch.py`.

## Root Cause

The transformers backend passes **3D tensors** `(batch, seq_len, hidden_dim)` through linear layers, but the conch kernel's `apply_weights` method forwards `x` directly to `mixed_precision_gemm`, which internally does `m_dim, k_dim = x.shape` — an unpacking that only works for 2D tensors.

Other mixed-precision kernel implementations (e.g., the machete kernel in the same directory) already handle this by reshaping to 2D before calling the GEMM and reshaping back afterward.

## Expected Behavior

`apply_weights` should accept tensors of any batch dimensionality (2D or 3D) and return an output tensor with matching batch dimensions.

## Relevant Files

- `vllm/model_executor/kernels/linear/mixed_precision/conch.py` — the `apply_weights` method
- `vllm/model_executor/kernels/linear/mixed_precision/machete.py` — reference implementation that already handles this correctly
