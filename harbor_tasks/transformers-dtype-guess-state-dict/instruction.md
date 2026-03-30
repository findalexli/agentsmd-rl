# Fix: dtype guessing from state dict returns float8/float4 dtypes that cannot be used as default dtype

## Problem

The `get_state_dict_dtype` function in `src/transformers/modeling_utils.py` returns the first floating-point dtype found in a model's state dict. When a model has weights stored in `float8_e4m3fn`, `float8_e5m2`, `float4_e2m1fn`, or similar exotic quantized dtypes, the function returns that dtype. However, PyTorch does not allow setting these dtypes as the default dtype (`torch.set_default_dtype`), which causes failures when attempting to instantiate a model under the guessed dtype.

This means models saved with float8 or float4 quantized weights cannot be loaded via `from_pretrained` because the dtype guessing logic selects an unusable dtype.

## Root Cause

The `get_state_dict_dtype` function iterates through all tensors in the state dict and returns the dtype of the first floating-point tensor it finds (using `t.is_floating_point()`). It does not filter out float8 and float4 dtypes, which are technically floating-point but cannot be used as PyTorch's default dtype for model instantiation. The function should skip these quantized float dtypes and continue searching for a standard floating-point dtype (like float16, bfloat16, or float32).

## File to Modify

- `src/transformers/modeling_utils.py` -- the `get_state_dict_dtype` function
