"""Tests for dagster-dlt local state drop fix.

These tests verify that the fix properly clears stale pipeline state before runs,
preventing interference from previous failed runs.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_PATH = Path("/workspace/dagster")


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


def test_drop_state_called():
    """Test that drop() is called during dagster-dlt runs.

    This test verifies that the fix calls drop() to clear local state.
    """
    test_code = '''
import sys
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

# Track whether drop was called
drop_calls = []

# Create pipeline
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

# Patch the pipeline drop method
original_drop = pipeline.drop

def patched_drop(*args, **kwargs):
    drop_calls.append("drop")
    return original_drop(*args, **kwargs)

pipeline.drop = patched_drop

try:
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

    # Verify that drop() was called
    if "drop" in drop_calls:
        print("SUCCESS: drop() was called as expected")
    else:
        print("FAIL: drop() was not called")
        sys.exit(1)
finally:
    # Restore original method
    pipeline.drop = original_drop
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


def test_repo_dagster_dlt_core_pipeline():
    """dagster-dlt core pipeline test passes (pass_to_pass).

    Runs a specific test that exercises the dlt pipeline run functionality
    through the DagsterDltResource, which is the component modified by the fix.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py::test_example_pipeline",
         "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Core pipeline test failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


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
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_dagster_core_imports():
    """Dagster core and dagster-dlt can be imported without errors (pass_to_pass).

    Verifies that the basic imports work, which validates the package
    installation and dependencies.
    """
    test_code = """
import dagster
import dagster_dlt
from dagster_dlt import DagsterDltResource, dlt_assets
print("SUCCESS: All imports work correctly")
"""
    r = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr[-500:]}"
    assert "SUCCESS" in r.stdout, "Imports did not complete successfully"


def test_repo_dagster_dlt_resource_import():
    """DagsterDltResource and related classes can be imported (pass_to_pass).

    Verifies that the resource module and its key classes are importable.
    """
    test_code = """
from dagster_dlt.resource import DagsterDltResource, DltEventIterator
from dagster_dlt import DagsterDltTranslator, dlt_assets
print("SUCCESS: Resource imports work correctly")
"""
    r = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Resource import test failed:\n{r.stderr[-500:]}"
    assert "SUCCESS" in r.stdout, "Resource imports did not complete successfully"
