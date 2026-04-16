"""
Tests for dagster-dlt drop local state fix.

These tests verify that dagster-dlt drops local pipeline state before running,
preventing stale state from interfering with subsequent runs.
"""

import os
import subprocess
import sys
import tempfile

import pytest

REPO = os.environ.get("REPO", "/workspace/dagster")


class TestDropLocalState:
    """Test that dagster-dlt drops local state before pipeline run."""

    def test_drop_clears_stale_pipeline_state(self):
        """
        Verify that when a DLT pipeline has stale normalized packages,
        running through dagster-dlt clears them and processes the real source.

        This test fails on base commit (no drop call) because stale state
        causes dlt to return early without processing the real source.
        """
        # Run the PR's test that validates the drop behavior
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py::test_drop_clears_stale_pipeline_state_before_run",
                "-v", "--tb=short"
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        # The test should pass when fix is applied
        # On base commit, this test doesn't exist, so pytest returns exit code 4
        # But we need to distinguish between "test doesn't exist" vs "test exists and fails"
        # Since the test IS added by the fix, on base commit it won't exist (4)
        # With fix applied, the test runs and passes (0)
        assert result.returncode == 0, (
            f"Test failed - stale pipeline state not being dropped.\n"
            f"stdout: {result.stdout[-1000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )

    def test_drop_pending_packages_when_restore_disabled(self):
        """
        Verify that when restore_from_destination is disabled,
        dagster-dlt drops only pending packages (not full state).

        This preserves incremental loading cursors while clearing
        extract/normalize state from failed runs.
        """
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py::test_drop_pending_packages_when_restore_from_destination_disabled",
                "-v", "--tb=short"
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, (
            f"Test failed - pending packages not being dropped correctly.\n"
            f"stdout: {result.stdout[-1000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )

    def test_dlt_resource_tests_pass(self):
        """
        Run the full dagster-dlt test suite for the resource and asset decorator.
        Ensures no regressions in DLT integration.
        """
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py",
                "-v", "--tb=short",
                "-x",  # Stop on first failure
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600
        )

        assert result.returncode == 0, (
            f"dagster-dlt test suite failed.\n"
            f"stdout: {result.stdout[-2000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )


class TestRepoCI:
    """Pass-to-pass tests from repo CI/CD."""

    def test_make_ruff(self):
        """Run make ruff on the dagster-dlt module (pass_to_pass)."""
        result = subprocess.run(
            ["make", "ruff", "python_modules/libraries/dagster-dlt/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, (
            f"make ruff failed on dagster-dlt.\n"
            f"stdout: {result.stdout[-1000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )

    def test_pytest_dlt_unit_tests(self):
        """Run dagster-dlt unit tests (pass_to_pass)."""
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "python_modules/libraries/dagster-dlt/dagster_dlt_tests/",
                "-v", "--tb=short",
                "-x",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600
        )

        assert result.returncode == 0, (
            f"dagster-dlt unit tests failed.\n"
            f"stdout: {result.stdout[-2000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )

    def test_ruff_format(self):
        """Run ruff format check on dagster-dlt module (pass_to_pass)."""
        result = subprocess.run(
            ["ruff", "format", "--check", "python_modules/libraries/dagster-dlt/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, (
            f"ruff format check failed on dagster-dlt.\n"
            f"stdout: {result.stdout[-1000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )

    def test_pytest_load_collection_component(self):
        """Run dagster-dlt load collection component tests (pass_to_pass)."""
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_dlt_load_collection_component.py",
                "-v", "--tb=short",
                "-x",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, (
            f"dagster-dlt load collection component tests failed.\n"
            f"stdout: {result.stdout[-2000:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )
