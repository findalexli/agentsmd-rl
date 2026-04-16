# Fix: SGLang metrics not uploaded to W&B in primary process

## Problem

In the THUDM/slime project, SGLang Prometheus metrics are not being uploaded to Weights & Biases (W&B) during training.

Currently, the SGLang metrics endpoint configuration is done inside the secondary W&B process (via `init_wandb_secondary` in `slime/utils/wandb_utils.py`). However, secondary W&B processes cannot run the stats monitor required for open metrics collection — only the primary process can.

The primary W&B run is initialized early in the training scripts (`train.py` and `train_async.py`) before rollout servers start, in order to obtain the run ID that secondary processes need. By the time rollout servers are running and the metrics router address is known, the primary W&B run has already been initialized without any metrics endpoint configuration.

## Expected Outcome

After the fix, the primary W&B process should be re-initialized with SGLang metrics endpoint scraping configured, once the rollout servers are up and the router address is available. The secondary process should no longer be responsible for metrics endpoint configuration.

## Relevant Code

- `slime/utils/wandb_utils.py` — Contains `init_wandb_primary` and `init_wandb_secondary`. The existing `init_wandb_secondary` function currently accepts a `router_addr` parameter and configures open metrics endpoints (using `x_stats_open_metrics_endpoints` with the `sgl_engine` key). This metrics configuration logic needs to move from the secondary to the primary process.
- `slime/utils/logging_utils.py` — Bridge layer between training scripts and W&B utilities (contains `init_tracking`, `finish_tracking`).
- `slime/ray/rollout.py` — Rollout manager class with a private `_get_metrics_router_addr` method that returns the SGLang router's address.
- `train.py` and `train_async.py` — Training entry points where W&B initialization and rollout manager creation happen.

## Behavioral Requirements

The solution must satisfy these contracts:

1. **Remove `router_addr` from secondary**: `init_wandb_secondary` in `wandb_utils.py` must no longer accept a `router_addr` parameter. It must remain functional for its other purposes (it should still have a non-trivial implementation).

2. **New re-init function**: A function named `reinit_wandb_primary_with_open_metrics` must be added to `wandb_utils.py`, accepting parameters `args` and `router_addr`. When `router_addr` is `None`, it must return early without making any W&B calls. When given a valid router address, it must re-initialize the existing primary W&B run with the SGLang metrics endpoint configured for scraping from the router. The implementation should be substantial (not a stub).

3. **Logging bridge**: A function named `update_tracking_open_metrics` must be added to `logging_utils.py`, accepting `args` and `router_addr`, that delegates to `reinit_wandb_primary_with_open_metrics`.

4. **Public rollout method**: The rollout manager class in `rollout.py` must expose a public method named `get_metrics_router_addr` that returns the metrics router address.

5. **Training script integration**: Both `train.py` and `train_async.py` must import and call `update_tracking_open_metrics` after the rollout manager is created, passing the router address.

All modified files must pass `ruff`, `black`, and `isort` checks.
