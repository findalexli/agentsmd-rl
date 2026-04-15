# Fix: SGLang metrics not uploaded to W&B in primary process

## Problem

SGLang Prometheus metrics are not being uploaded to W&B (Weights & Biases) during training. The metrics endpoint configuration is happening in the wrong W&B process, causing the stats monitor to miss SGLang metrics.

The issue is a sequencing problem:
1. The primary W&B run is initialized early in the training script (before rollout servers start) to obtain the run ID for secondary processes
2. By the time the rollout servers are running and the SGLang metrics router address is known, the primary W&B run is already initialized without the metrics endpoint configured
3. Secondary W&B processes cannot run the stats monitor needed for open metrics collection

## Technical Requirements

To fix this issue, the following behavioral requirements must be met:

1. **Secondary process changes**: The secondary W&B initialization function should not accept a `router_addr` parameter, since secondary processes cannot run the stats monitor.

2. **Primary process re-initialization**: A function named `reinit_wandb_primary_with_open_metrics` must be created that accepts `args` and `router_addr` parameters. This function must:
   - Return early without touching wandb when `router_addr` is `None`
   - Call `wandb.finish()` before `wandb.init()` to close the existing run
   - Use `resume="allow"` in the init kwargs to continue the same run
   - Configure `wandb.Settings` with `x_stats_open_metrics_endpoints` containing `"sgl_engine": f"{router_addr}/engine_metrics"`

3. **Logging utilities bridge**: The logging utilities module must expose a function named `update_tracking_open_metrics(args, router_addr)` that delegates to `reinit_wandb_primary_with_open_metrics`.

4. **Rollout manager API**: The rollout manager class must expose a public method `get_metrics_router_addr()` that returns the metrics router address (wrapping the private `_get_metrics_router_addr` method).

5. **Training script updates**: The training entry points must import `update_tracking_open_metrics` and call it after the rollout manager is created, passing the router address obtained via `ray.get(rollout_manager.get_metrics_router_addr.remote())`.
