# Bug: Mamba cudagraph capture sizes silently capped, degrading prefill performance

## Description

In `vllm/v1/worker/gpu_model_runner.py`, the method `_check_and_update_cudagraph_mode` handles hybrid Mamba/attention models by calling `adjust_cudagraph_sizes_for_mamba_cache` on the compilation config. This function silently modifies the shared `cudagraph_capture_sizes` list, which restricts **both** PIECEWISE (prefill) and FULL (decode) cudagraph captures.

However, the Mamba cache constraint only applies to FULL decode graphs. The PIECEWISE path runs Mamba ops eagerly and is unaffected. By silently capping the shared sizes, prefill cudagraphs are unnecessarily restricted, causing them to fall back to eager mode and severely degrading performance.

Additionally, this check runs during profiling (via `_init_minimal_kv_cache_for_profiling`), where the minimal cache block count is artificially low — leading to incorrect capping even for the decode path.

## What should happen

Instead of silently capping cudagraph capture sizes (which affects both prefill and decode paths), the system should:

1. Only validate that enough Mamba cache blocks exist for FULL decode graphs (where `max_num_seqs` determines the maximum batch size)
2. Raise an informative error if there aren't enough blocks, rather than silently degrading performance
3. Skip this validation during profiling, since the profiling phase uses artificially small cache configurations

## Relevant files

- `vllm/v1/worker/gpu_model_runner.py` — `_check_and_update_cudagraph_mode`, `initialize_kv_cache`, `initialize_attn_backend`, `_init_minimal_kv_cache_for_profiling`
- `vllm/config/compilation.py` — `adjust_cudagraph_sizes_for_mamba_cache` method on `CompilationConfig`

## Hints

- The FULL decode cudagraph dispatcher in `vllm/v1/cudagraph_dispatcher.py` already filters decode capture sizes to `<= max_num_seqs * uniform_decode_query_len`, so the real safety check is simply whether `max_num_seqs <= num_blocks`
- The `adjust_cudagraph_sizes_for_mamba_cache` method and its tests should be removed since the approach of silently capping sizes is fundamentally wrong
- A profiling flag needs to be threaded through the call chain to skip validation during dummy cache creation
