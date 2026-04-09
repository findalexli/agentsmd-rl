# Add Error Handling to Trajectory Processing

## Problem

The trajectory processing functions (`interleave_rollout` and `branch_rollout` in `src/prime_rl/orchestrator/trajectories.py`) currently don't handle two important edge cases:

1. **Empty trajectories**: When a rollout has no trajectory steps, the functions crash when trying to access `trajectory[0]`.

2. **Error states**: When a rollout has an error set in `state["error"]`, the current code still uses the original completion mask values. However, errored rollouts should be masked out (completion_mask set to all False) so they don't contribute to training.

Additionally, the orchestrator in `src/prime_rl/orchestrator/orchestrator.py` uses a local helper `get_is_truncated()` to detect truncated rollouts, but the verifiers library now provides this information directly in `rollout["is_truncated"]`.

## Expected Behavior

1. `interleave_rollout` and `branch_rollout` should return `None` when given a state with an empty trajectory (and log a warning). The orchestrator should skip such rollouts when building training examples.

2. Both functions should check for `state["error"]` and zero out the `completion_mask` (set all values to False) when an error is present. This masks out errored rollouts from training.

3. The orchestrator should use `rollout["is_truncated"]` directly instead of calling `get_is_truncated()`, and should log error metrics (`error/mean` and per-error-type rates).

4. **Config update**: Along with the code changes, add new configuration files for the `math_python` environment:
   - Create `configs/math_python/math_python.toml` with RL training settings
   - Create `configs/math_python/README.md` with setup and usage instructions
   - Update `CHANGELOG.md` with the relevant changes
   - Update `pyproject.toml` to bump the `verifiers` dependency revision

## Files to Look At

- `src/prime_rl/orchestrator/trajectories.py` — Core trajectory processing functions that need error handling
- `src/prime_rl/orchestrator/orchestrator.py` — Orchestrator that uses trajectory functions and logs metrics
- `tests/unit/orchestrator/test_trajectories.py` — Test fixtures that need the `error` field added
- `configs/math_python/` — New directory for math_python config (to be created)
- `CHANGELOG.md` — Documentation of changes
- `pyproject.toml` — Dependency management

## Notes

- The `verifiers` library provides `vf.State` which now includes an `error` field and `is_truncated` field
- The `TrainingSample` struct is defined in `src/prime_rl/transport/types.py`
- Look at existing config files in `configs/` for patterns to follow
