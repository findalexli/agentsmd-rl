# Fix: Drop dlt local state before run

## Problem

The `dagster-dlt` integration has an issue where dlt's local state from previous runs can interfere with new runs. This happens when:

1. A pipeline run fails or is interrupted after extraction/normalization but before loading
2. Stale normalized packages remain in the local state
3. Subsequent runs pick up these stale packages and either fail or return early without processing the real source

This is particularly problematic in orchestrated environments like Dagster+ where the same pipeline instance may be reused across different asset materializations.

## What You Need to Do

Find where the dagster-dlt integration manages dlt pipeline execution. Before the pipeline runs the source data through, you need to clear any stale local state from previous runs.

The fix should handle two cases based on the pipeline's configuration:

1. When the pipeline is configured to restore state from the destination (`restore_from_destination=True`, which is the default behavior), all local state can be safely cleared because it will be restored from the destination.

2. When the pipeline is configured to NOT restore state from the destination (`restore_from_destination=False`), only pending packages should be cleared. This avoids wiping incremental loading cursors that cannot be recovered from the destination.

The dlt library provides methods to clear this state - refer to the dlt pipeline API documentation for the appropriate methods to drop state and/or pending packages.

## Requirements

After your fix:
- `dlt_pipeline.drop()` must be called when `restore_from_destination` is True
- `dlt_pipeline.drop_pending_packages()` must be called when `restore_from_destination` is False
- These calls must happen before the pipeline's `run()` method is invoked
- Stale state from previous failed runs must not interfere with subsequent runs
- All existing dagster-dlt tests must continue to pass
- Ruff linting and formatting checks must pass

## Background

The dlt library maintains local state including extracted and normalized data packages. In normal dlt usage, this is fine because dlt manages the full lifecycle. However, when used with an orchestrator like Dagster:

- The pipeline object may be reused across multiple runs
- Failed runs can leave stale packages behind
- These stale packages interfere with subsequent runs, causing them to process old data or fail entirely

The fix should be applied within the dagster-dlt resource where the pipeline execution is managed.
