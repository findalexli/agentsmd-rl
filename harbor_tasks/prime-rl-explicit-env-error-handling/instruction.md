# Explicitly handle + log env errors

## Problem

The PRIME-RL orchestrator needs to properly handle environment errors that occur during rollouts. Currently, when a rollout encounters an error (e.g., infrastructure failure, tool call error), the system doesn't gracefully handle these cases:

1. The `interleave_rollout()` and `branch_rollout()` functions in `trajectories.py` don't handle empty trajectories or error states - they should return `None` for empty trajectories and mask out completion tokens when an error occurred.

2. The orchestrator doesn't safely handle cases where `make_train_example()` might return `None` - it tries to iterate over the result without checking.

3. The orchestrator uses a local `get_is_truncated()` function instead of using the `is_truncated` field directly from the rollout data provided by verifiers.

4. Error metrics aren't being logged - we need to track the error rate and distribution of error types.

## Expected Behavior

1. `interleave_rollout()` and `branch_rollout()` should:
   - Return `None` when the trajectory is empty (with a warning log)
   - Zero out all `completion_mask` entries when `state["error"]` is set
   - Have updated type annotations: `list[TrainingSample] | None`

2. The orchestrator should:
   - Safely check if `train_example` is `None` before iterating
   - Use `rollout["is_truncated"]` directly instead of `get_is_truncated(rollout)`
   - Log error metrics including overall error rate and per-error-type distribution

3. Update the test fixtures in `tests/unit/orchestrator/test_trajectories.py` to include `error=None` in the mock state objects.

## Files to Look At

- `src/prime_rl/orchestrator/trajectories.py` — The `interleave_rollout()` and `branch_rollout()` functions need to handle empty trajectories and error states.

- `src/prime_rl/orchestrator/orchestrator.py` — The orchestrator needs to safely handle `None` returns, use rollout's `is_truncated` field directly, and log error metrics.

- `tests/unit/orchestrator/test_trajectories.py` — Test fixtures need to be updated with `error=None` field.

## Additional Context

This PR integrates changes from the verifiers library that now provides explicitly defined exceptions and per-env configurable errors. The rollout data now includes an `error` field that should be checked and handled appropriately.
