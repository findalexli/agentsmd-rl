# Qwen3.5 Pipeline Parallelism: Mamba Cache and MoE Weight Loading Bugs

## Context

SGLang supports pipeline parallelism (PP) for distributing model layers across multiple GPUs. Each PP rank handles a contiguous range of layers defined by `start_layer` and `end_layer`. The Qwen3.5 model family uses a hybrid architecture combining Mamba (linear attention) layers and standard attention layers, along with Mixture-of-Experts (MoE).

## Bug 1: Mamba Cache Not Sharded for PP

When creating the hybrid memory pools for Mamba cache, the code allocates memory for **all** Mamba layers in the model, regardless of which PP rank is running. This means each rank wastes GPU memory by allocating cache for layers it doesn't own.

The issue is in `python/sglang/srt/mem_cache/memory_pool.py`:
- `HybridReqToTokenPool` and `MambaPool` use the full list of layer IDs from `cache_params.layers` instead of filtering to only the layers within the current PP rank's range.
- The `start_layer` is hardcoded to `0` in multiple places (look for `# TODO: Support PP` comments).
- Similarly, `HybridLinearKVPool` hardcodes `start_layer = 0`.

The pool initialization code in `python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py` creates these pools but doesn't pass the PP rank boundaries.

## Bug 2: MoE Weight Loading Failure in PP Mode

When loading Qwen3.5 MoE models with pipeline parallelism, the `load_weights` and `load_fused_expert_weights` methods in `python/sglang/srt/models/qwen3_5.py` attempt to load **all** layer weights, including layers outside the current PP rank's range. This causes a `KeyError` because `params_dict` only contains parameters for the layers assigned to this rank.

The model has multiple classes that need this fix:
- `Qwen3_5ForCausalLM` (around line 1013)
- `Qwen3_5MoeForCausalLM` (around line 1094 and 1140)
- `Qwen3_5VLForConditionalGeneration` (around line 1332 and 1477)

Additionally, `python/sglang/srt/models/qwen3_vl.py` has a `Qwen3VLForConditionalGeneration` class that already has PP-aware weight skipping in its `load_weights` method, but it accesses `self.model.start_layer` / `self.model.end_layer` directly. The Qwen3.5 VL model class needs similar property accessors to delegate to the inner model's layer boundaries.

## Expected Behavior

1. Mamba cache pools should only allocate memory for layers within the current PP rank's `[start_layer, end_layer)` range.
2. Weight loading should skip any layer whose ID falls outside the current rank's range.
3. The `start_layer` for cache pools should be passed from the model runner, not hardcoded to 0.

## Error (Bug 2)

```
KeyError: 'model.layers.21.mlp.experts.w2_weight'
```

This occurs when a PP rank tries to load expert weights for a layer it doesn't own.
