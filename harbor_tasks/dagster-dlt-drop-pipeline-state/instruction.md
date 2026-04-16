# Fix dlt Local State Interference in Dagster Integration

## Problem

The dagster-dlt integration has a bug where dlt's local state persists between pipeline runs, causing subsequent executions to fail with stale state from previous runs. When an asset fails during execution and a different asset is run on the same pipeline, the new run picks up the failing state and also fails.

The dlt library maintains internal state (normalized packages, pending jobs) that carries over between pipeline executions within the DagsterDltResource.

## Relevant dlt Pipeline API

The dlt `Pipeline` object provides these state management methods:

- `drop()` — clears all local pipeline state
- `drop_pending_packages()` — clears only pending packages, preserving incremental loading cursors

The pipeline configuration has a `restore_from_destination` setting (enabled by default). When enabled, state can be fully cleared since it will be restored from the destination. When disabled, only pending packages should be cleared to preserve incremental loading cursors that cannot be recovered.

## Requirements

Fix the state interference bug. The fix must:

1. Clear stale local state before each pipeline's `run()` call
2. Handle both `restore_from_destination` modes appropriately — full state clear when enabled, partial clear when disabled
3. Include an explanatory comment containing: `Dlt keeps some local state that interferes with next runs`
4. Include a comment for the enabled case: `restore_from_destination is enabled (default)`
5. Include a comment for the disabled case: `restore_from_destination is disabled`

## Verification

After making changes:
- Run `make ruff` to check code style
- Run the dagster-dlt unit tests
- Verify the dagster_dlt module imports without errors
