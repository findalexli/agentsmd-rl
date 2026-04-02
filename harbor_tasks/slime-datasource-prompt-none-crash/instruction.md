# Bug: RolloutDataSource crashes when no dataset path is provided

## Summary

When running SLIME's rollout pipeline with global dataset mode enabled but without actually providing a dataset path, the `RolloutDataSource` class in `slime/rollout/data_source.py` crashes during initialization. The constructor unconditionally attempts to load a dataset without first checking whether the path is valid.

Additionally, other methods on `RolloutDataSource` don't properly handle the case where the internal dataset object was never created. Querying the length of the data source and restoring from a checkpoint both crash with unhandled exceptions under this scenario.

## Separately: Router health check not disabled

In `slime/ray/rollout.py`, the function that launches the router configures several router arguments (e.g., the circuit breaker is disabled for disaggregation scenarios) but does not similarly disable the router's built-in health check. The health check can produce spurious failure signals during normal operation and should be disabled for all router launches.

## Relevant files

- `slime/rollout/data_source.py` — `RolloutDataSource` class
- `slime/ray/rollout.py` — router launch configuration

## Reproduction

1. Configure a rollout with global dataset mode on, but leave the dataset path unset
2. Instantiate the data source — crashes trying to load from an invalid path
3. Even if initialization is bypassed, querying the data source length raises a `TypeError`
4. Loading a checkpoint with shuffling enabled raises an `AttributeError` on the uninitialized dataset
