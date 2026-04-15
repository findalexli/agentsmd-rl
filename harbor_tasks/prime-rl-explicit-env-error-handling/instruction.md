# Explicitly handle + log env errors

## Problem

The PRIME-RL orchestrator needs to properly handle environment errors that occur during rollouts. Currently, when a rollout encounters an error (e.g., infrastructure failure, tool call error), the system doesn't gracefully handle these cases:

1. Rollout processing functions crash or return incorrect results when the trajectory is empty, and they don't mask completion tokens when an error occurred.

2. The orchestrator crashes when `make_train_example()` returns `None` — it tries to iterate over the result without checking.

3. The orchestrator calls a helper function to detect truncation instead of reading a field directly from the rollout data.

4. Error metrics aren't being logged — we need to track the error rate and distribution of error types.

## Expected Behavior

1. The rollout processing functions should:
   - Return `None` when the trajectory is empty (with a warning log)
   - Zero out all `completion_mask` entries when `state["error"]` is set
   - Have return type annotations that include `None` as a possible return value

2. The orchestrator should:
   - Check if `train_example` is `None` before iterating over it
   - Access the truncation status directly from the rollout data structure
   - Log error metrics including overall error rate and per-error-type distribution

3. Test fixtures in `tests/unit/orchestrator/test_trajectories.py` should include `error=None` in the mock state objects.

## Files to Look At

- `src/prime_rl/orchestrator/trajectories.py` — Functions that convert rollout state to training samples
- `src/prime_rl/orchestrator/orchestrator.py` — The main orchestrator loop
- `tests/unit/orchestrator/test_trajectories.py` — Unit test fixtures

## Additional Context

This PR integrates changes from the verifiers library that now provides explicitly defined exceptions and per-env configurable errors. The rollout data now includes an `error` field that should be checked and handled appropriately.

## Verification Criteria

### Import Statement
The import statement beginning with `from prime_rl.utils.vf` should not include any `get_is_truncated` reference.

### Type Annotations
The rollout processing functions must have their return type annotated using Python 3.10+ union syntax with the `|` operator. The pattern `-> list[TrainingSample] | None:` should appear in the function signatures.

### Error Masking
When a trajectory has an error (i.e., `state["error"]` is not `None`), all `completion_mask` values in the resulting samples must be `False`.

### None Handling
The orchestrator must check `if train_example is not None:` before iterating over the train examples.

### Truncation Field
The orchestrator should access the truncation status using the subscript operator directly on the rollout object (e.g., `rollout["is_truncated"]` or `rollout['is_truncated']`), not via a helper function.
