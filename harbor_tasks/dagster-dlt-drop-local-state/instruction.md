# Fix: Drop dlt local state before run

## Problem

The `dagster-dlt` integration has an issue where dlt's local state from previous runs can interfere with new runs. This happens when:

1. A pipeline run fails or is interrupted after extraction/normalization but before loading
2. Stale normalized packages remain in the local state
3. Subsequent runs pick up these stale packages and either fail or return early without processing the real source

This is particularly problematic in orchestrated environments like Dagster+ where the same pipeline instance may be reused across different asset materializations.

## What You Need to Do

Find where the dagster-dlt integration manages dlt pipeline execution. Before the pipeline runs the source data through, you need to clear any stale local state from previous runs.

The dlt library maintains local state including extracted and normalized data packages. In normal dlt usage, this is fine because dlt manages the full lifecycle. However, when used with an orchestrator like Dagster:

- The pipeline object may be reused across multiple runs
- Failed runs can leave stale packages behind
- These stale packages interfere with subsequent runs, causing them to process old data or fail entirely

You should use the dlt pipeline API to clear this stale state before the pipeline's `run()` method is invoked. The dlt library provides pipeline management methods that can handle this - consult the dlt pipeline API documentation to find the appropriate methods for your pipeline configuration.

Note that the `restore_from_destination` setting affects how state is managed, so ensure your fix accounts for this configuration.

## Requirements

After your fix:
- Stale state from previous failed runs must not interfere with subsequent runs
- The fix must handle both cases where state restoration is enabled and disabled
- All existing dagster-dlt tests must continue to pass
- Ruff linting and formatting checks must pass

## Background

The fix should be applied within the dagster-dlt resource where the pipeline execution is managed. Look for where the dlt pipeline's `run()` method is called and ensure that stale state is cleared before that call.
