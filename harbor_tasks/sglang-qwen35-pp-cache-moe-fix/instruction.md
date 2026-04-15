# Qwen3.5 Pipeline Parallelism: Mamba Cache and MoE Weight Loading Bugs

## Context

SGLang supports pipeline parallelism (PP) for distributing model layers across multiple GPUs. Each PP rank handles a contiguous range of layers defined by `start_layer` and `end_layer`. The Qwen3.5 model family uses a hybrid architecture combining Mamba (linear attention) layers and standard attention layers, along with Mixture-of-Experts (MoE).

## Bug 1: Mamba Cache Not Sharded for PP

When creating the hybrid memory pools for Mamba cache, the code allocates memory for **all** Mamba layers in the model, regardless of which PP rank is running. This means each rank wastes GPU memory by allocating cache for layers it doesn't own.

The affected components are:
- `HybridReqToTokenPool` and `MambaPool` in the memory pool code — these pool classes allocate cache based on layer IDs passed to them, but the layer IDs must be filtered to only include layers within the current PP rank's range
- `HybridLinearKVPool` — similarly uses `start_layer` which needs to be parametric (not hardcoded to 0)
- Pool initialization in the model runner — must pass PP rank boundaries to the pools

The `start_layer` value passed to cache pools should reflect the current rank's starting layer, not be hardcoded to 0.

## Bug 2: MoE Weight Loading Failure in PP Mode

When loading Qwen3.5 MoE models with pipeline parallelism, the `load_weights` and `load_fused_expert_weights` methods attempt to load **all** layer weights, including layers outside the current PP rank's range. This causes a `KeyError` because `params_dict` only contains parameters for the layers assigned to this rank.

The weight loading methods must skip any weight whose layer ID falls outside the current rank's `[start_layer, end_layer)` range. A utility function that extracts the layer ID from a weight name (e.g., `model.layers.21.mlp.experts.w2_weight` → `21`) is needed to implement this filtering.

The error manifests as:
```
KeyError: 'model.layers.21.mlp.experts.w2_weight'
```

This occurs when a PP rank tries to load expert weights for a layer it doesn't own.

## Required Fixes

1. **Create a `get_layer_id` utility function** in `python/sglang/srt/layers/utils/common.py` that extracts the integer layer ID from weight parameter names. It should:
   - Return the layer number when given a weight like `model.layers.21.mlp.gate_proj.weight`
   - Return `None` for non-layer weights like `model.embed_tokens.weight` or `lm_head.weight`

2. **Modify weight loading in Qwen3.5 models** to use `get_layer_id` for PP-aware filtering. In `load_weights` and `load_fused_expert_weights` methods, skip weights whose layer ID is outside `[start_layer, end_layer)`.

3. **Make cache pool initialization PP-aware** by passing the PP rank's layer boundaries. The pools must accept filtered layer ID lists and a `start_layer` parameter instead of hardcoding `start_layer=0`.

4. **Add `start_layer`/`end_layer` properties to Qwen3.5 VL wrapper classes** that delegate to the inner model, so the weight loading filtering can work through the wrapper.

## Expected Behavior

1. Mamba cache pools should only allocate memory for layers within the current PP rank's `[start_layer, end_layer)` range.
2. Weight loading should skip any layer whose ID falls outside the current rank's range — no `KeyError` should occur.
3. The `start_layer` for cache pools should be passed from the model runner, derived from the PP rank configuration.
