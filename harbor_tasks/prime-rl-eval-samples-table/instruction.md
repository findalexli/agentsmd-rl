# Missing eval rollout logging in monitor interface

## Context

The `prime-rl` training framework has a monitor interface (`src/prime_rl/utils/monitor/base.py`) that abstracts logging to various backends (W&B, Prime, no-op). Training rollouts are already logged to a "samples" table via `Monitor.log_samples()`, allowing developers to inspect individual completions during training.

However, the **online evaluation** path (`src/prime_rl/orchestrator/eval_utils.py`, function `evaluate_env`) only logs aggregate metrics (mean reward, pass@k, completion length, etc.). The individual eval rollout outputs — which include per-example completions, rewards, and task IDs — are computed but never logged for inspection.

## Problem

After an eval run completes, there is no way to inspect individual eval completions. Only summary statistics are recorded. This makes it difficult to debug evaluation failures or understand why certain examples score poorly.

The monitor interface (`Monitor` base class in `base.py`) has abstract methods for logging training samples (`log_samples`) and final samples (`log_final_samples`), but no equivalent for evaluation samples. The `evaluate_env` function in `eval_utils.py` calls `monitor.log()` for metrics but does not log the individual rollout outputs through the monitor interface.

## Requirements

The monitor interface needs to support logging evaluation samples, following the same pattern used for training samples (`log_samples`). Specifically:

1. **Monitor ABC**: The `Monitor` base class needs a new abstract method `log_eval_samples` for logging eval rollouts. It should accept the rollout outputs, the environment name, and the current step.

2. **All concrete implementations must implement the new method**:
   - `NoOpMonitor` (in `base.py`) — should accept calls without error, as a no-op
   - `MultiMonitor` (in `multi.py`) — should delegate to all sub-monitors, consistent with how it handles other logging methods
   - `WandbMonitor` (in `wandb.py`) — should log eval samples to a W&B table (see below)
   - `PrimeMonitor` (in `prime.py`) — should implement the method (a no-op stub is acceptable)

3. **WandbMonitor table logging**: The `WandbMonitor` implementation should record eval samples into a dedicated W&B table (separate from the training samples table) with the following columns: `step`, `env`, `task`, `example_id`, `completion`, `reward`. Each rollout with a non-empty completion should become a row in the table. Rollouts where the `completion` field is empty or missing should be skipped (not added to the table). The table should be logged to W&B after processing the rollouts.

4. **evaluate_env integration**: The `evaluate_env` function should invoke the new eval sample logging through the monitor after logging metrics, passing along the rollout outputs, environment name, and step.

## Relevant files

- `src/prime_rl/utils/monitor/base.py` — `Monitor` ABC and `NoOpMonitor`
- `src/prime_rl/utils/monitor/multi.py` — `MultiMonitor` (delegates to sub-monitors)
- `src/prime_rl/utils/monitor/wandb.py` — `WandbMonitor` (W&B logging)
- `src/prime_rl/utils/monitor/prime.py` — `PrimeMonitor`
- `src/prime_rl/orchestrator/eval_utils.py` — `evaluate_env` function
