"""Tests for dagster-dlt local state drop fix.

These tests verify that the fix properly clears stale pipeline state before runs,
preventing interference from previous failed runs.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_PATH = Path("/workspace/dagster")


def test_drop_state_with_restore_from_destination():
    """Test that drop() is called when restore_from_destination is enabled (default).

    This test verifies the fix for the case where restore_from_destination=True.
    In this case, we can safely drop all local state since it will be restored
    from the destination.
    """
    test_code = '''
import tempfile
import os
import dlt
from dagster import materialize, AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets
from dagster_dlt.translator import DagsterDltTranslator, DltResourceTranslatorData
from dagster import AssetSpec

# Create a simple pipeline for testing
@dlt.source
def test_source():
    @dlt.resource
    def test_data():
        yield {"id": 1, "value": "test"}
    return test_data

# Track whether drop was called
drop_calls = []
original_drop = None

def patched_drop(self, *args, **kwargs):
    drop_calls.append("drop")
    return original_drop(self, *args, **kwargs)

def patched_drop_pending(self, *args, **kwargs):
    drop_calls.append("drop_pending_packages")
    # Don't actually call the original to avoid side effects
    return None

# Patch the pipeline methods
import dlt.pipeline.pipeline
original_drop = dlt.pipeline.pipeline.Pipeline.drop
original_drop_pending = dlt.pipeline.pipeline.Pipeline.drop_pending_packages
dlt.pipeline.pipeline.Pipeline.drop = patched_drop
dlt.pipeline.pipeline.Pipeline.drop_pending_packages = patched_drop_pending

try:
    # Create pipeline with restore_from_destination=True (default)
    pipeline = dlt.pipeline(
        pipeline_name="test_pipeline",
        destination="duckdb",
        dataset_name="test_dataset",
    )

    # First run to populate the destination
    pipeline.run(test_source())

    # Create stale normalized packages
    @dlt.source
    def stale_source():
        @dlt.resource
        def stale_data():
            yield {"id": 1, "value": "stale"}
        return stale_data

    pipeline.extract(stale_source())
    pipeline.normalize()

    # Now define dagster assets
    @dlt_assets(dlt_source=test_source(), dlt_pipeline=pipeline)
    def test_assets(context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource):
        yield from dlt_pipeline_resource.run(context=context)

    res = materialize(
        [test_assets],
        resources={"dlt_pipeline_resource": DagsterDltResource()},
    )

    # Verify success
    assert res.success, "Materialization should succeed"

    # Verify that drop() was called (not drop_pending_packages)
    # After the fix, drop() should be called when restore_from_destination=True
    if "drop" in drop_calls:
        print("SUCCESS: drop() was called as expected")
    elif "drop_pending_packages" in drop_calls:
        print("FAIL: drop_pending_packages() was called instead of drop()")
        sys.exit(1)
    else:
        # Neither was called - the fix might not be applied
        print("FAIL: Neither drop() nor drop_pending_packages() was called")
        sys.exit(1)
finally:
    # Restore original methods
    dlt.pipeline.pipeline.Pipeline.drop = original_drop
    dlt.pipeline.pipeline.Pipeline.drop_pending_packages = original_drop_pending
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120,
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "SUCCESS: drop() was called as expected" in result.stdout


def test_drop_pending_packages_when_restore_disabled():
    """Test that drop_pending_packages() is called when restore_from_destination is False.

    This test verifies the fix for the case where restore_from_destination=False.
    In this case, we should only drop pending packages to avoid wiping
    incremental loading cursors that can't be recovered from the destination.
    """
    test_code = '''
import tempfile
import os
import dlt
from dagster import materialize, AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets

# Create a simple pipeline for testing
@dlt.source
def test_source():
    @dlt.resource
    def test_data():
        yield {"id": 1, "value": "test"}
    return test_data

# Track method calls
drop_calls = []
original_drop = None
original_drop_pending = None

def patched_drop(self, *args, **kwargs):
    drop_calls.append("drop")
    return original_drop(self, *args, **kwargs)

def patched_drop_pending(self, *args, **kwargs):
    drop_calls.append("drop_pending_packages")
    # Don't actually call original to avoid side effects
    return None

# Patch the pipeline methods
import dlt.pipeline.pipeline
original_drop = dlt.pipeline.pipeline.Pipeline.drop
original_drop_pending = dlt.pipeline.pipeline.Pipeline.drop_pending_packages
dlt.pipeline.pipeline.Pipeline.drop = patched_drop
dlt.pipeline.pipeline.Pipeline.drop_pending_packages = patched_drop_pending

try:
    # Create pipeline with restore_from_destination=False
    pipeline = dlt.pipeline(
        pipeline_name="test_pipeline_disabled",
        destination="duckdb",
        dataset_name="test_dataset",
    )
    pipeline.config.restore_from_destination = False

    # Create stale packages
    @dlt.source
    def stale_source():
        @dlt.resource
        def stale_data():
            yield {"id": 1, "value": "stale"}
        return stale_data

    pipeline.extract(stale_source())
    pipeline.normalize()

    # Define dagster assets
    @dlt_assets(dlt_source=test_source(), dlt_pipeline=pipeline)
    def test_assets_disabled(context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource):
        yield from dlt_pipeline_resource.run(context=context)

    res = materialize(
        [test_assets_disabled],
        resources={"dlt_pipeline_resource": DagsterDltResource()},
    )

    assert res.success, "Materialization should succeed"

    # When restore_from_destination=False, drop_pending_packages() should be called
    if "drop_pending_packages" in drop_calls:
        print("SUCCESS: drop_pending_packages() was called as expected")
    elif "drop" in drop_calls:
        print("FAIL: drop() was called instead of drop_pending_packages()")
        sys.exit(1)
    else:
        print("FAIL: Neither drop() nor drop_pending_packages() was called")
        sys.exit(1)
finally:
    # Restore original methods
    dlt.pipeline.pipeline.Pipeline.drop = original_drop
    dlt.pipeline.pipeline.Pipeline.drop_pending_packages = original_drop_pending
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120,
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "SUCCESS: drop_pending_packages() was called as expected" in result.stdout


def test_stale_state_interference_regression():
    """Regression test: verify that stale state from previous runs doesn't interfere.

    This test simulates the bug scenario where a failed run leaves stale
    normalized packages, and a subsequent run should not be affected.
    """
    test_code = '''
import dlt
from dagster import materialize, AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets

@dlt.source
def good_source():
    @dlt.resource
    def good_data():
        for i in range(5):
            yield {"id": i, "value": f"good_{i}"}
    return good_data

@dlt.source
def stale_source():
    @dlt.resource
    def stale_data():
        yield {"id": 999, "value": "stale"}
    return stale_data

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name="interference_test",
    destination="duckdb",
    dataset_name="test_dataset",
)

# First run to populate destination
pipeline.run(good_source())

# Simulate a "failed" run that leaves stale state
# (extract + normalize but no load)
pipeline.extract(stale_source())
pipeline.normalize()

# Without the fix, this stale state would interfere with the next run
@dlt_assets(dlt_source=good_source(), dlt_pipeline=pipeline)
def test_assets(context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource):
    yield from dlt_pipeline_resource.run(context=context)

res = materialize(
    [test_assets],
    resources={"dlt_pipeline_resource": DagsterDltResource()},
)

assert res.success, "Materialization should succeed despite stale state"
print("SUCCESS: Stale state did not interfere with the run")
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120,
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "SUCCESS: Stale state did not interfere with the run" in result.stdout


# --- Pass-to-pass tests: repo CI/CD checks that must pass on both base and fix ---


def test_repo_dagster_dlt_tests():
    """dagster-dlt test suite passes (pass_to_pass).

    Runs the repo's own pytest suite for the dagster-dlt module to ensure
    existing functionality is not broken by changes.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "python_modules/libraries/dagster-dlt/dagster_dlt_tests/",
         "-x", "-q"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"dagster-dlt tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ruff_check():
    """Ruff lint check on dagster-dlt passes (pass_to_pass).

    Runs `ruff check` on the dagster-dlt module to ensure no lint violations.
    """
    r = subprocess.run(
        ["ruff", "check", "python_modules/libraries/dagster-dlt/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Ruff format check on dagster-dlt passes (pass_to_pass).

    Runs `ruff format --check` on the dagster-dlt module to ensure
    code formatting is correct.
    """
    r = subprocess.run(
        ["ruff", "format", "--check", "python_modules/libraries/dagster-dlt/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}""
