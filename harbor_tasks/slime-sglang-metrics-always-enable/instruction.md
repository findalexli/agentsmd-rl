# SGLang Metrics Endpoint Not Always Available for W&B Scraping

## Bug Description

The SGLang engine's Prometheus metrics endpoint (`/engine_metrics`) is not reliably available for W&B (Weights & Biases) metrics scraping. The endpoint is only activated when a specific CLI flag is passed, even though the metrics infrastructure is always running and the endpoint should always be accessible.

There are three related issues across the metrics pipeline:

1. **`slime/backends/sglang_utils/sglang_engine.py`**: The `_compute_server_args` function builds the server configuration but does not unconditionally enable the Prometheus metrics endpoint. The server arguments allowlist also omits the relevant key, so it would be silently dropped even if set externally. Additionally, prefill workers use an incorrect load-balancing method.

2. **`slime/ray/rollout.py`**: The `_get_metrics_router_addr` method has an early-return guard that checks a CLI flag before returning the router address. When the flag is unset (the common case), the method returns `None`, which silently disables W&B metrics forwarding even when a valid router address exists.

3. **`slime/utils/wandb_utils.py`**: The `init_wandb_secondary` function gates the Open Metrics forwarding setup behind the same CLI flag. Even when a valid `router_addr` is provided, metrics are not forwarded unless the flag is explicitly set.

A secondary issue is in `slime/rollout/sglang_rollout.py`: the `GenerateState` class contains dead code for DP (data-parallel) rank balancing — a context manager and associated bookkeeping that is no longer needed since the engine handles DP scheduling itself. This dead code wraps the generation logic in an unnecessary context manager, adding complexity.

## Expected Behavior

- The Prometheus metrics endpoint should always be enabled in the server configuration, without requiring a CLI flag.
- W&B metrics forwarding should activate whenever a valid router address is available.
- Dead DP-rank balancing code should be removed to simplify the rollout path.

## Files to Investigate

- `slime/backends/sglang_utils/sglang_engine.py` — `_compute_server_args()` and the server args allowlist
- `slime/ray/rollout.py` — `_get_metrics_router_addr()`
- `slime/utils/wandb_utils.py` — `init_wandb_secondary()`
- `slime/rollout/sglang_rollout.py` — `GenerateState` class and `generate_and_rm()`
