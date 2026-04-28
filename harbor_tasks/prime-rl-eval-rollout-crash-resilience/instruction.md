# Evaluation crashes when individual rollout groups fail

## Problem

The evaluation pipeline in `src/prime_rl/orchestrator/vf_utils.py` runs rollout groups concurrently using `asyncio.gather`. If any single group raises an exception during execution (e.g., network timeout, model error, OOM), the exception propagates and crashes the entire evaluation run. This means one bad group out of hundreds can take down the whole eval.

Additionally, in `src/prime_rl/orchestrator/eval_utils.py`, when all rollouts fail or return nothing, downstream code tries to build a DataFrame from an empty list and compute metrics on it, which produces confusing errors instead of a clean early exit.

## Expected behavior

- A single group failure should not crash the entire evaluation
- Failed groups should be logged as warnings and excluded from results
- If all rollouts fail for an environment, the function should log a warning and return early rather than crashing on empty data
- Successful groups should still return their results normally

## Files to investigate

- `src/prime_rl/orchestrator/vf_utils.py` -- the concurrent group execution in the evaluation flow; look at how `asyncio.gather` is used with individual group tasks
- `src/prime_rl/orchestrator/eval_utils.py` -- the `evaluate_env()` function; look at what happens when the outputs list is empty

## Code Style Requirements

- All code must pass `ruff check` and `ruff format --check` with the project's configuration in `pyproject.toml`
- Exception handlers must use specific exception types; bare `except:` clauses are not allowed per the project's AGENTS.md guidelines
- Do not add explanatory comments that reference old code or describe the change process ("used to", "changed from", "previously", etc.)
- Errors should never pass silently — failures must be logged as warnings
