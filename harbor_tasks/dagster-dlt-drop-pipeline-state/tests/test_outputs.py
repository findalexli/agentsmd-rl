"""Tests for dagster-dlt pipeline state fix.

This tests that the dagster-dlt resource properly clears local pipeline state
before runs to prevent interference from stale data.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/dagster")
DAGSTER_DLT_PATH = REPO / "python_modules/libraries/dagster-dlt"


def test_drop_pipeline_state_code_exists():
    """F2P: Verify the fix code exists in resource.py.

    The fix adds pipeline.drop() or drop_pending_packages() calls
    before running the pipeline to clear stale state.
    """
    resource_file = DAGSTER_DLT_PATH / "dagster_dlt/resource.py"
    content = resource_file.read_text()

    # Check that the fix is present
    assert "dlt_pipeline.drop()" in content, "Missing dlt_pipeline.drop() call"
    assert "drop_pending_packages()" in content, "Missing drop_pending_packages() call"
    assert "restore_from_destination" in content, "Missing restore_from_destination check"


def test_drop_behavior_with_restore_enabled():
    """F2P: Verify drop() is called when restore_from_destination is enabled.

    When restore_from_destination is True (default), the full drop() should be
    called to clear all local state since it will be restored from destination.
    """
    resource_file = DAGSTER_DLT_PATH / "dagster_dlt/resource.py"
    content = resource_file.read_text()

    # Find the _run method and check the logic structure
    # The fix should have:
    # if dlt_pipeline.config.restore_from_destination:
    #     dlt_pipeline.drop()
    # else:
    #     dlt_pipeline.drop_pending_packages()

    lines = content.split("\n")
    found_restore_check = False
    found_drop_call = False
    found_drop_pending_call = False
    in_run_method = False
    indent_level = 0

    for i, line in enumerate(lines):
        # Detect entry into _run method (approximate)
        if "def _run(" in line:
            in_run_method = True
            continue

        if in_run_method:
            # Look for the restore_from_destination check
            if "if dlt_pipeline.config.restore_from_destination:" in line:
                found_restore_check = True
                indent_level = len(line) - len(line.lstrip())
                # Check next few lines for drop() call
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent > indent_level and "dlt_pipeline.drop()" in next_line:
                        found_drop_call = True
                    if next_indent > indent_level and "dlt_pipeline.drop_pending_packages()" in next_line:
                        found_drop_pending_call = True

            # Look for else clause with drop_pending_packages
            if "else:" in line and found_restore_check:
                indent_level = len(line) - len(line.lstrip())
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent > indent_level and "dlt_pipeline.drop_pending_packages()" in next_line:
                        found_drop_pending_call = True

    assert found_restore_check, "Missing restore_from_destination conditional check"
    assert found_drop_call, "Missing dlt_pipeline.drop() in if branch"
    assert found_drop_pending_call, "Missing dlt_pipeline.drop_pending_packages() in else branch"


def test_comment_documentation_present():
    """F2P: Verify the explanatory comment is present."""
    resource_file = DAGSTER_DLT_PATH / "dagster_dlt/resource.py"
    content = resource_file.read_text()

    # Check for the explanatory comment
    assert "Dlt keeps some local state that interferes with next runs" in content
    assert "restore_from_destination is enabled (default)" in content
    assert "restore_from_destination is disabled" in content


def test_drop_called_before_run():
    """F2P: Verify drop/drop_pending_packages is called before load_info is assigned.

    The fix must call drop() BEFORE dlt_pipeline.run() is called,
    not after. This test verifies the order is correct.
    """
    resource_file = DAGSTER_DLT_PATH / "dagster_dlt/resource.py"
    content = resource_file.read_text()

    # Find the _run method and verify order
    lines = content.split("\n")
    drop_line_idx = None
    run_line_idx = None
    load_info_line_idx = None

    for i, line in enumerate(lines):
        if "dlt_pipeline.drop()" in line or "dlt_pipeline.drop_pending_packages()" in line:
            drop_line_idx = i
        if "dlt_pipeline.run(dlt_source" in line:
            run_line_idx = i
        if "load_info = dlt_pipeline.run" in line:
            load_info_line_idx = i

    # The drop calls must exist
    assert drop_line_idx is not None, "No drop() or drop_pending_packages() call found"
    assert run_line_idx is not None or load_info_line_idx is not None, "No run() call found"

    # Drop must come before run
    target_run_idx = run_line_idx if run_line_idx is not None else load_info_line_idx
    assert drop_line_idx < target_run_idx, "drop() must be called BEFORE dlt_pipeline.run()"


# =============================================================================
# Pass-to-Pass Tests (Regression/Sanity Checks)
# =============================================================================


def test_repo_ruff_dagster_dlt():
    """P2P: Run ruff check on dagster-dlt package (pass_to_pass).

    Verifies the dagster-dlt package passes linting, a lightweight CI check
    that ensures the fix doesn't introduce code style violations.
    Runs the repo's actual linting command.
    """
    # Install ruff with correct version (matching repo's Makefile)
    result = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    result = subprocess.run(
        ["python", "-m", "ruff", "check", str(DAGSTER_DLT_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_dagster_dlt_unit_tests():
    """P2P: Run dagster-dlt unit tests (pass_to_pass).

    Runs a curated subset of the repo's own tests that exercise the
    DagsterDltResource to verify the fix doesn't break existing functionality.
    """
    # Install pytest and duckdb if needed
    subprocess.run(
        ["pip", "install", "pytest", "duckdb", "-q"],
        capture_output=True,
        timeout=60,
    )

    # Use full paths to test files
    test_paths = [
        f"{DAGSTER_DLT_PATH}/dagster_dlt_tests/test_asset_decorator.py::test_example_pipeline",
        f"{DAGSTER_DLT_PATH}/dagster_dlt_tests/test_asset_decorator.py::test_example_pipeline_asset_keys",
        f"{DAGSTER_DLT_PATH}/dagster_dlt_tests/test_asset_decorator.py::test_example_pipeline_deps",
        f"{DAGSTER_DLT_PATH}/dagster_dlt_tests/test_op.py::test_base_dlt_op",
        f"{DAGSTER_DLT_PATH}/dagster_dlt_tests/test_version.py::test_version",
    ]

    env = {**os.environ, "PYTHONPATH": f"{DAGSTER_DLT_PATH}:{REPO / 'python_modules/dagster'}"}

    result = subprocess.run(
        ["python", "-m", "pytest", "-x", "-v"] + test_paths,
        capture_output=True,
        text=True,
        cwd=str(REPO),
        env=env,
        timeout=300,
    )

    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_make_check_ruff():
    """P2P: Run make check_ruff on the repo (pass_to_pass).

    Verifies the entire repo passes linting using the repo's Makefile target,
    ensuring the fix doesn't introduce any code style violations.
    """
    # Install ruff with correct version
    subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        timeout=60,
    )

    result = subprocess.run(
        ["make", "check_ruff"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=120,
    )

    assert result.returncode == 0, f"make check_ruff failed:\n{result.stdout}\n{result.stderr}"


def test_dagster_dlt_import():
    """P2P: Verify dagster_dlt imports correctly (pass_to_pass).

    Basic smoke test that the dagster_dlt module can be imported
    without errors after the fix.
    """
    result = subprocess.run(
        ["python", "-c", "from dagster_dlt import DagsterDltResource; print('Import OK')"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=30,
    )

    assert result.returncode == 0, f"Import failed:\n{result.stderr}"
    assert "Import OK" in result.stdout
