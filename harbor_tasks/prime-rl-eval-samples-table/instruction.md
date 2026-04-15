# Missing eval rollout logging in monitor interface

## Context

The `prime-rl` training framework has a monitor interface (`src/prime_rl/utils/monitor/base.py`) that abstracts logging to various backends (W&B, Prime, no-op). Training rollouts are already logged to a "samples" table via `Monitor.log_samples()`, allowing developers to inspect individual completions during training.

However, the **online evaluation** path (`src/prime_rl/orchestrator/eval_utils.py`, function `evaluate_env`) only logs aggregate metrics (mean reward, pass@k, completion length, etc.). The individual eval rollout outputs — which include per-example completions, rewards, and task IDs — are computed but never logged for inspection.

## Problem

After an eval run completes, there is no way to inspect individual eval completions. Only summary statistics are recorded. This makes it difficult to debug evaluation failures or understand why certain examples score poorly.

The monitor interface (`Monitor` base class) has methods for logging training samples (`log_samples`) and final samples (`log_final_samples`), but no equivalent for evaluation samples. The `evaluate_env` function calls `monitor.log()` for metrics but does not log the individual rollout outputs.

## What needs to change

1. The `Monitor` abstract base class needs a new abstract method for logging eval samples with the signature:
   `log_eval_samples(self, rollouts: list[RolloutOutput], env_name: str, step: int) -> None`
2. All concrete monitor implementations (`NoOpMonitor`, `MultiMonitor`, `WandbMonitor`, `PrimeMonitor`) need to implement this method
3. The `WandbMonitor` implementation should log eval samples to a dedicated W&B table (separate from the training samples table) with columns: `step`, `env`, `task`, `example_id`, `completion`, `reward`. Rollouts with empty or missing `completion` fields should not be added to the table.
4. The `evaluate_env` function should call `monitor.log_eval_samples(outputs, env_name=env_name, step=step)` after logging metrics

## Relevant files

- `src/prime_rl/utils/monitor/base.py` — `Monitor` ABC and `NoOpMonitor`
- `src/prime_rl/utils/monitor/multi.py` — `MultiMonitor` (delegates to sub-monitors)
- `src/prime_rl/utils/monitor/wandb.py` — `WandbMonitor` (W&B logging)
- `src/prime_rl/utils/monitor/prime.py` — `PrimeMonitor`
- `src/prime_rl/orchestrator/eval_utils.py` — `evaluate_env` function
