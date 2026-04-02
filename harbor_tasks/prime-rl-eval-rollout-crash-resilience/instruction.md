# Evaluation crashes when individual rollout groups fail

## Problem

The evaluation pipeline in `src/prime_rl/orchestrator/vf_utils.py` runs rollout groups concurrently using `asyncio.gather`. If any single group raises an exception during execution (e.g., network timeout, model error, OOM), the exception propagates through `asyncio.gather` and crashes the entire evaluation run. This means one bad group out of hundreds can take down the whole eval.

The `generate()` function's inner `run_group_with_progress()` coroutine calls `run_group()` directly without any error isolation. When gathered, a single failure causes all other concurrent groups to be effectively wasted since the whole gather raises.

Additionally, in `src/prime_rl/orchestrator/eval_utils.py`, the `evaluate_env()` function doesn't handle the case where the outputs list is empty. If all rollouts fail or return nothing, downstream code tries to build a DataFrame from an empty list and compute metrics on it, which produces confusing errors instead of a clean early exit.

## Expected behavior

- A single group failure should not crash the entire evaluation
- Failed groups should be logged as warnings and excluded from results
- If all rollouts fail for an environment, the function should log a warning and return early rather than crashing on empty data

## Files to investigate

- `src/prime_rl/orchestrator/vf_utils.py` -- `generate()` function and its inner `run_group_with_progress()` coroutine
- `src/prime_rl/orchestrator/eval_utils.py` -- `evaluate_env()` function
