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

## Areas to Investigate

The config definitions for inference deployment live in the `src/prime_rl/configs/` directory. SLURM script generation entry points are in `src/prime_rl/entrypoints/`. Jinja2 templates for SLURM jobs are in `src/prime_rl/templates/`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
