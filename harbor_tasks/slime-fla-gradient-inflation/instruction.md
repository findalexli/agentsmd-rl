# SP/CP gradient inflation in FLA (linear attention) layers

## Problem

In `slime_plugins/models/hf_attention.py`, the `HuggingfaceAttention.forward()` method has two gradient-inflation bugs that cause inflated gradient norms when using Sequence Parallelism (SP) and/or Context Parallelism (CP) with linear attention (FLA) layers:

### Bug 1: SP gather backward inflates gradients by TP

The call to `tensor_parallel.gather_from_sequence_parallel_region()` uses the default `tensor_parallel_output_grad=True`. This means the backward pass performs a reduce-scatter, summing `TP` identical copies of the gradient. Since the linear attention computation after the gather is NOT TP-sharded (it is duplicated across ranks), the backward should split the gradient instead, which requires `tensor_parallel_output_grad=False`.

### Bug 2: CP all_gather backward inflates gradients by CP

The call to `dist.nn.all_gather()` performs a reduce-scatter in its backward pass. Since the computation after the gather is duplicated across CP ranks (same weights, same full input producing identical gradients), the reduce-scatter incorrectly sums `CP` identical copies, inflating the gradient by the CP size.

### Additional issues in related files

- `slime_plugins/models/qwen3_5.py` and `slime_plugins/models/qwen3_next.py` contain duplicated or missing `_load_hf_config` functionality and lack a `layer_types` fallback for configs that do not expose this attribute (causing `AttributeError` for Qwen3.5 and Qwen3Next models).

- `hf_attention.py` uses `from transformers import AutoConfig` directly which fails for unsupported model types. A `_load_hf_config` helper with a fallback is needed.

## Expected Behavior

- The SP gather should use `tensor_parallel_output_grad=False` so its backward splits instead of reduce-scattering.
- The CP gather should use a custom autograd function whose backward returns only the local gradient slice (no reduce).
- `_load_hf_config` should be consolidated in `hf_attention.py` with a fallback for unsupported model types.
- `layer_types` should be computed from `full_attention_interval` when not available on the config.

## Files to Modify

- `slime_plugins/models/hf_attention.py` -- fix gather backward behavior, add `_load_hf_config`, add `_AllGatherForDuplicatedComputation`
- `slime_plugins/models/qwen3_5.py` -- use shared `_load_hf_config`, add `layer_types` fallback
- `slime_plugins/models/qwen3_next.py` -- use shared `_load_hf_config`, add `layer_types` fallback
- `slime/utils/reloadable_process_group.py` -- adjust memory threshold
