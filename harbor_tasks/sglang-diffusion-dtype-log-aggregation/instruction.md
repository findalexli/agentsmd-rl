# Bug: Excessive per-parameter dtype mismatch warnings during weight loading

## Context

The diffusion model weight loader in `python/sglang/multimodal_gen/runtime/loader/fsdp_load.py` is responsible for loading checkpoint weights into the model. When the checkpoint dtype doesn't match the model's expected dtype (e.g., `float32` checkpoint loaded into a `bfloat16` model), the loader emits a warning for each mismatched parameter.

## Problem

When loading a model with many parameters that have dtype mismatches, the `load_model_from_full_model_state_dict` function emits an individual `logger.warning(...)` call **for every single parameter** that has a dtype mismatch. For large diffusion models with hundreds or thousands of parameters, this floods the log with repetitive messages like:

```
Dtype mismatch for blocks.0.ffn.fc_out.bias: checkpoint has torch.float32, model expects torch.bfloat16. Casting checkpoint tensor to the target dtype during load.
Dtype mismatch for blocks.0.ffn.fc_out.weight: checkpoint has torch.float32, model expects torch.bfloat16. Casting checkpoint tensor to the target dtype during load.
Dtype mismatch for blocks.0.norm_k.weight: checkpoint has torch.float32, model expects torch.bfloat16. Casting checkpoint tensor to the target dtype during load.
... (hundreds more identical-pattern lines)
```

This makes logs very noisy and hard to read, burying actually important warnings.

## Expected behavior

- Non-quantized dtype mismatches (e.g., float32→bfloat16) should be **aggregated** into a single summary log message after loading completes, rather than one message per parameter. A few example parameter names per mismatch type is sufficient.
- Quantized dtype mismatches (involving uint8, float8, int8) should similarly be aggregated but logged at warning level since they may indicate real issues.
- The `_QUANTIZED_DTYPES` tuple is currently re-defined inside the loop on every iteration — it should be moved to module scope.

## Files to modify

- `python/sglang/multimodal_gen/runtime/loader/fsdp_load.py`
