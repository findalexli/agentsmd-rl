# SGLang Metrics Endpoint Not Always Available for W&B Scraping

## Bug Description

The SGLang engine's Prometheus metrics endpoint (`/engine_metrics`) is not reliably available for W&B (Weights & Biases) metrics scraping. The endpoint is only activated when a specific CLI flag is passed, even though the metrics infrastructure should always be accessible.

There are several related issues across the metrics pipeline:

1. **Server configuration in `slime/backends/sglang_utils/sglang_engine.py`**: The server arguments builder needs to unconditionally enable the Prometheus metrics endpoint by setting `enable_metrics=True` in the server kwargs. Additionally, the `enable_metrics` key must be added to the `_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS` allowlist so it is not silently dropped. A related configuration issue: prefill workers are configured with an incorrect load-balancing method; they should use `follow_bootstrap_room` instead of `round_robin`.

2. **Router address retrieval in `slime/ray/rollout.py`**: The method that returns the metrics router address has an early-return guard that checks a CLI flag (`sglang_enable_metrics`) before returning the address. When the flag is unset, the method returns `None`, which silently disables W&B metrics forwarding even when a valid router address exists. This guard should be removed so the router address is returned whenever available.

3. **W&B initialization in `slime/utils/wandb_utils.py`**: The Open Metrics forwarding setup is gated behind the same CLI flag. Even when a valid router address is provided, metrics are not forwarded unless the flag is explicitly set. The forwarding should activate based on the presence of the router address, not the CLI flag.

4. **Dead code in `slime/rollout/sglang_rollout.py`**: The `GenerateState` class contains unused code for DP (data-parallel) rank balancing — a context manager method `dp_rank_context` and associated bookkeeping (`dp_counts`, `dp_rank`) that is no longer needed since the engine handles DP scheduling itself. This dead code should be removed, including the `from contextlib import contextmanager` import which was only used by this feature.

## Expected Behavior

- The Prometheus metrics endpoint should always be enabled in the server configuration via `enable_metrics=True`
- The `_EXTERNAL_ENGINE_SKIP_CHECK_FIELDS` allowlist must include `enable_metrics`
- Prefill workers should use `follow_bootstrap_room` as the load-balance method
- W&B metrics forwarding should activate whenever a valid router address is available, without requiring a CLI flag
- Dead DP-rank balancing code (the `dp_rank_context` method, related instance variables, and the `contextmanager` import) should be removed

## Files to Investigate

- `slime/backends/sglang_utils/sglang_engine.py` — server configuration and allowlist
- `slime/ray/rollout.py` — router address retrieval
- `slime/utils/wandb_utils.py` — W&B metrics forwarding setup
- `slime/rollout/sglang_rollout.py` — `GenerateState` class
