# Evaluation crashes when individual rollout groups fail

## Problem

The evaluation pipeline in `src/prime_rl/orchestrator/vf_utils.py` runs rollout groups concurrently using `asyncio.gather`. If any single group raises an exception during execution (e.g., network timeout, model error, OOM), the exception propagates and crashes the entire evaluation run. This means one bad group out of hundreds can take down the whole eval.

Additionally, in `src/prime_rl/orchestrator/eval_utils.py`, when all rollouts fail or return nothing, downstream code tries to build a DataFrame from an empty list and compute metrics on it, which produces confusing errors instead of a clean early exit.

## Expected behavior

- A single group failure should not crash the entire evaluation
- Failed groups should be logged as warnings and excluded from results
- If all rollouts fail for an environment, the function should log a warning and return early rather than crashing on empty data

## Files to investigate

- `src/prime_rl/orchestrator/vf_utils.py` -- the concurrent group execution in the evaluation flow
- `src/prime_rl/orchestrator/eval_utils.py` -- the `evaluate_env()` function
