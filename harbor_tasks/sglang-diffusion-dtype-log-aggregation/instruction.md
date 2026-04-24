# Bug: Excessive per-parameter dtype mismatch warnings during weight loading

## Context

When loading diffusion model checkpoint weights, dtype mismatches between the checkpoint and the model (e.g., `float32` checkpoint loaded into a `bfloat16` model) cause per-parameter warnings that flood the logs. Each individual warning contains the text `"Dtype mismatch for"` followed by the parameter name and dtype details, producing output like:

```
Dtype mismatch for blocks.0.ffn.fc_out.bias: checkpoint has torch.float32, model expects torch.bfloat16. Casting checkpoint tensor to the target dtype during load.
Dtype mismatch for blocks.0.ffn.fc_out.weight: checkpoint has torch.float32, model expects torch.bfloat16. Casting checkpoint tensor to the target dtype during load.
Dtype mismatch for blocks.0.norm_k.weight: checkpoint has torch.float32, model expects torch.bfloat16. Casting checkpoint tensor to the target dtype during load.
... (hundreds more identical-pattern lines)
```

## Problem

The weight loader for diffusion models emits an individual `logger.warning(...)` call **for every single parameter** that has a dtype mismatch. For large models with hundreds or thousands of mismatched parameters, this makes logs extremely noisy, burying actually important warnings.

Additionally, the main loading loop has an efficiency issue: constant values (including any values related to quantized dtypes, identifiable by variable names containing `'quantiz'`) are being re-created inside the loop body on every pass rather than being defined once outside the loop.

## Expected behavior

1. **Remove per-parameter dtype mismatch warnings from the loading loop.** The main parameter loading loop in `load_model_from_full_model_state_dict` must not call `logger.warning` with any string containing the literal text `"Dtype mismatch for"` for individual parameters.

2. **Add a module-level summary formatter function.** Create a new module-level function (defined at module scope, outside any existing function, and not named `_make_param_like`, `load_model_from_full_model_state_dict`, or `shard_model`) that formats aggregated dtype mismatch summaries. The function must:
   - Accept a `collections.Counter` as its first argument, keyed by `(checkpoint_dtype, target_dtype)` tuples, where values are integer counts of parameters with that mismatch pair
   - Accept a `collections.defaultdict(list)` (or equivalent dict) as its second argument, keyed by the same `(checkpoint_dtype, target_dtype)` tuples, where values are lists of example parameter name strings
   - Return a human-readable string that:
     - Includes the numeric count for each dtype mismatch pair (e.g., the strings `"50"`, `"12"`, or `"100"`)
     - Includes the dtype names (e.g., `"float32"`, `"bfloat16"`, `"float16"`, `"int8"`)
     - Includes example parameter names when available (e.g., `"blocks.0.weight"`, `"blocks.1.bias"`, `"embed.pos"`, `"fc.weight"`, `"fc.bias"`)
     - Handles the case where the example list is empty (still showing the count and dtype)
     - Does NOT contain raw `Counter(` or `defaultdict(` repr strings

3. **Emit aggregated summary logs after the loading loop completes.** After the main parameter loading loop finishes, log aggregated dtype mismatch summaries. The logging call (on `logger`) should appear after the loop ends (at a line number greater than the loop's end line) and the call or its arguments should contain at least one of these keywords: `'dtype'`, `'mismatch'`, `'cast'`, or `'summary'`.
   - Non-quantized dtype mismatches (e.g., float32→bfloat16) should be aggregated and logged at debug level
   - Quantized dtype mismatches (involving uint8, float8, int8) should be aggregated and logged at warning level

4. **Avoid re-creating loop-invariant values inside the loop.** Any values that do not depend on the loop variable and remain constant across all iterations must be defined at a broader scope (e.g., module level or before the loop), not assigned inside the loop body. Specifically, no variable with `'quantiz'` in its name (case-insensitive) should be assigned a value inside the loading loop.

## Target file

`python/sglang/multimodal_gen/runtime/loader/fsdp_load.py`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black (Python formatter)`
