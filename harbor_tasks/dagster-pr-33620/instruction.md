# Dagster DLT Local State Issue

## Problem

The Dagster DLT integration has a bug where local pipeline state persists between runs, causing unexpected behavior.

When using Dagster to orchestrate DLT pipelines, if an asset fails mid-execution, running a different asset on the same pipeline will fail because DLT's local state from the previous (failed) run interferes with the new execution. DLT may skip processing or load stale job state instead of the actual source data.

This is problematic in development (where pipelines are run repeatedly) and in hybrid Dagster+ deployments with local agents.

## Requirements

Fix the dagster-dlt integration to clear local state before executing a pipeline. The fix must handle two different configurations:

- When `restore_from_destination` is enabled (the default): Clear all local state, since the destination has the authoritative data and can restore the state
- When `restore_from_destination` is disabled: Only clear pending packages, preserving incremental loading cursors that can't be recovered from the destination

## Verification

After fixing, ensure:
1. Stale pipeline state does not block execution of assets on the same pipeline
2. Incremental loading behavior is preserved when `restore_from_destination` is disabled
3. The existing test suite passes
4. Code follows repository conventions (type hints, `@record` usage, etc.)

Add the following tests to `python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py`:

- `test_drop_clears_stale_pipeline_state_before_run` - Verify that when a DLT pipeline has stale normalized packages, running through dagster-dlt clears them and processes the real source
- `test_drop_pending_packages_when_restore_from_destination_disabled` - Verify that when `restore_from_destination` is disabled, dagster-dlt only clears pending packages (not full state) to preserve incremental loading cursors

Run `make ruff` on the dagster-dlt module after making changes.
