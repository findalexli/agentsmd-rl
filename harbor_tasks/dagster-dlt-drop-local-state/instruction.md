# Fix: Drop dlt local state before run

## Problem

The `dagster-dlt` integration has an issue where dlt's local state from previous runs can interfere with new runs. This happens when:

1. A pipeline run fails or is interrupted after extraction/normalization but before loading
2. Stale normalized packages remain in the local state
3. Subsequent runs pick up these stale packages and either fail or return early without processing the real source

This is particularly problematic in orchestrated environments like Dagster+ where the same pipeline instance may be reused across different asset materializations.

## Files to Modify

- `python_modules/libraries/dagster-dlt/dagster_dlt/resource.py`

## What You Need to Do

Find the `_run` method in the `DagsterDltResource` class. Before calling `dlt_pipeline.run()`, you need to clear any stale local state from previous runs:

1. When `dlt_pipeline.config.restore_from_destination` is `True` (the default), call `dlt_pipeline.drop()` to clear all local state. This is safe because the state will be restored from the destination.

2. When `dlt_pipeline.config.restore_from_destination` is `False`, call `dlt_pipeline.drop_pending_packages()` instead. This clears pending packages without wiping incremental loading cursors that can't be recovered from the destination.

## Background

The dlt library maintains local state including extracted and normalized data packages. In normal dlt usage, this is fine because dlt manages the full lifecycle. However, when used with an orchestrator like Dagster:

- The pipeline object may be reused across multiple runs
- Failed runs can leave stale packages behind
- These stale packages interfere with subsequent runs, causing them to process old data or fail entirely

The fix should be applied just before the `dlt_pipeline.run()` call in the `_run` method.
