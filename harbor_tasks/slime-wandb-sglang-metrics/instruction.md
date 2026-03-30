# Fix: SGLang metrics not uploaded to W&B in primary process

## Problem

SGLang Prometheus metrics are not being uploaded to W&B (Weights & Biases) during training. The metrics scraping was configured in the secondary W&B process (rollout worker), but the open metrics endpoint requires being set up on the primary W&B run for the stats monitor to work.

## Root Cause

The primary W&B init happens in `train.py` before rollout servers start (to obtain `wandb_run_id` for secondary processes). By the time the rollout servers are up and the router address is available for scraping SGLang metrics, the primary W&B run has already been initialized without metrics endpoints. The secondary process tried to configure the endpoints via `router_addr` parameter to `init_wandb_secondary`, but secondary processes cannot run the stats monitor for open metrics.

## Expected Behavior

1. Remove `router_addr` from `init_wandb_secondary` -- secondary processes should not configure metrics endpoints
2. Add a `reinit_wandb_primary_with_open_metrics` function that re-initializes the primary W&B run after servers are up, with the router metrics endpoint configured
3. Expose a public `get_metrics_router_addr()` on the rollout manager for the driver process
4. Call the re-init from `train.py` and `train_async.py` after the rollout manager is created

## Files to Modify

- `slime/utils/wandb_utils.py` -- add reinit function, remove router_addr from secondary
- `slime/utils/logging_utils.py` -- add update_tracking_open_metrics
- `slime/ray/rollout.py` -- expose public get_metrics_router_addr, remove router_addr from init_tracking
- `train.py` and `train_async.py` -- call update after rollout manager creation
