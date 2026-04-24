# Handle Environment Errors in Rollout Processing

## Problem

The PRIME-RL orchestrator encounters runtime issues when processing rollouts that have error states. When infrastructure failures, tool call errors, or other environment errors occur during rollouts, the system exhibits the following problems:

1. **Empty trajectory crash**: The trajectory processing functions crash with an `IndexError` when given an empty trajectory, rather than gracefully handling the empty case.

2. **Error state not reflected in training masks**: When a rollout has encountered an error (indicated by a non-`None` value in the error field), the training samples produced still have their `completion_mask` values set to `True`, which can cause invalid training data to be used.

3. **None propagation crash**: The orchestrator crashes with a `TypeError` when iterating over the result of `make_train_example()` because it does not anticipate `None` as a possible return value.

4. **Incorrect truncation detection**: The orchestrator uses an indirect helper function to determine truncation status instead of reading the field directly from the rollout data.

5. **Missing error visibility**: Error occurrences are not logged as metrics, making it impossible to monitor error rates and distributions in production.

## Expected Behavior

When processing rollouts with the `interleave_rollout` and `branch_rollout` functions in `src/prime_rl/orchestrator/trajectories.py`, and when iterating over results in `src/prime_rl/orchestrator/orchestrator.py`, the system should:

- Handle empty trajectories gracefully (returning `None` rather than crashing)
- When the state contains a non-`None` error value, produce training samples with all `completion_mask` values set to `False`
- Include `None` as a possible return type for the trajectory processing functions using Python 3.10+ union syntax with the `|` operator
- Guard iteration over `make_train_example()` results with a `None` check before looping
- Read the `is_truncated` field directly from rollout data structures rather than through a helper function
- Log error metrics showing overall error rate and per-error-type distribution

## Test Fixture Requirements

The test fixtures in `tests/unit/orchestrator/test_trajectories.py` must include an `error` field (set to `None`) in all mock state objects, as the trajectory processing functions now need to handle this field.

## Verification Criteria

The solution will be verified against the following checks:

1. The `interleave_rollout` function signature must include the parameter `(state: vf.State)` and return type annotation using the `|` union operator with `None` as a possible return value.

2. The `branch_rollout` function signature must similarly include the parameter `(state: vf.State)` and return type annotation using the `|` union operator with `None` as a possible return value.

3. When a state has a non-`None` error field, all resulting `completion_mask` values must be `False`.

4. The orchestrator must check for `None` before iterating over `make_train_example()` results.

5. The orchestrator must access truncation status directly via subscript on the rollout object (e.g., `rollout["is_truncated"]` or `rollout['is_truncated']`), not via a helper function call.

6. The import statement beginning with `from prime_rl.utils.vf` must not reference `get_is_truncated`.

7. Error metrics must be logged, including the overall error rate and distribution of error types.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
