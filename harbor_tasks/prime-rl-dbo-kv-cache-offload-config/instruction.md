# Add DBO toggle and CPU KV-cache offloading config for disaggregated inference

## Problem

The `InferenceConfig` is missing a way to enable vLLM's dual batch overlap (DBO) feature. There is no `enable_dbo` field, and `to_vllm()` does not forward it to the vLLM namespace, so users cannot toggle DBO through the prime-rl config system.

Additionally, disaggregated prefill/decode deployments have no way to configure CPU KV-cache offloading. Prefill nodes should optionally use a `MultiConnector` (combining `NixlConnector` + `OffloadingConnector`) instead of the default `NixlConnector`-only setup, but the `DisaggregatedInferenceDeploymentConfig` has no field to express this.

The SLURM templates and entrypoint scripts also need updating to pass the new KV-cache offload parameters through to the Jinja2 templates and to differentiate between prefill and decode KV connector configurations.

## Expected Behavior

1. `InferenceConfig` should have an `enable_dbo` boolean field (default `False`) that is forwarded to the vLLM namespace via `to_vllm()`.

2. A new `KVCacheOffloadConfig` pydantic model should exist with `block_size` (int, >= 1, default 64) and `cpu_bytes` (int, >= 0, default 1,000,000,000) fields.

3. `DisaggregatedInferenceDeploymentConfig` should have a `kv_cache_offload` field (optional, default `None`) of type `KVCacheOffloadConfig`.

4. The inference and RL entrypoint `write_slurm_script` functions should pass the KV offload parameters to the template context.

5. The SLURM Jinja2 templates should use separate `PREFILL_KV_CFG` and `DECODE_KV_CFG` variables, with prefill nodes optionally using `MultiConnector` when KV offloading is enabled.

## Files to Look At

- `src/prime_rl/configs/inference.py` -- config classes for inference deployment
- `src/prime_rl/entrypoints/inference.py` -- SLURM script generation for inference
- `src/prime_rl/entrypoints/rl.py` -- SLURM script generation for RL training
- `src/prime_rl/templates/inference.sbatch.j2` -- disaggregated inference SLURM template
- `src/prime_rl/templates/multi_node_rl.sbatch.j2` -- multi-node RL SLURM template
