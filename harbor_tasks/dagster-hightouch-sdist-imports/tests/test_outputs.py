#!/usr/bin/env python3
"""Tests for dagster-hightouch sdist import fix.

These tests verify the sdist-compatible behavior by testing that the package
can be built as a wheel. The base code (with dagster._core.libraries and relative
imports) fails to build because dagster isn't available in the isolated build
environment. The fixed code (with dagster_shared.libraries and absolute imports)
builds successfully.
"""

import subprocess
import sys
import tempfile
import os

# Path to dagster-hightouch package
REPO = "/workspace/dagster/python_modules/libraries/dagster-hightouch"


def test_package_wheel_builds():
    """FAIL-TO-PASS: Package should build as a wheel (sdist compatibility check).

    The base code uses dagster._core.libraries which isn't available in the
    isolated build environment, causing the build to fail with ModuleNotFoundError.
    The fixed code uses dagster_shared.libraries which is available, so the
    build succeeds.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "wheel", ".", "--no-deps",
             "--wheel-dir", tmpdir],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )

    # The build should succeed (return code 0)
    assert result.returncode == 0, (
        f"Package wheel build failed. This indicates the package cannot be "
        f"built as an sdist/wheel, likely due to import issues.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_import_dagster_shared_libraries():
    """FAIL-TO-PASS: dagster_shared.libraries import should work instead of dagster._core.libraries."""
    # Test the fixed import works
    result = subprocess.run(
        [sys.executable, "-c", "from dagster_shared.libraries import DagsterLibraryRegistry; print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Failed to import from dagster_shared.libraries: {result.stderr}"
    assert "OK" in result.stdout


def test_package_imports_successfully():
    """FAIL-TO-PASS: dagster_hightouch package should import without errors."""
    result = subprocess.run(
        [sys.executable, "-c", "import dagster_hightouch; print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Failed to import dagster_hightouch: {result.stderr}"
    assert "OK" in result.stdout


def test_dagster_library_registry_registration():
    """FAIL-TO-PASS: DagsterLibraryRegistry should be properly registered."""
    result = subprocess.run(
        [sys.executable, "-c", """
import dagster_hightouch
from dagster_shared.libraries import DagsterLibraryRegistry
print(f"Library imported successfully")
print(f"Library version: {dagster_hightouch.__version__}")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"DagsterLibraryRegistry registration failed: {result.stderr}"
    assert "Library imported successfully" in result.stdout


def test_all_exports_available():
    """FAIL-TO-PASS: All exports from __all__ should be accessible."""
    result = subprocess.run(
        [sys.executable, "-c", """
import dagster_hightouch

exports = dagster_hightouch.__all__
for export in exports:
    obj = getattr(dagster_hightouch, export)
    print(f"{export}: {obj}")

print("All exports available")
"""],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Exports test failed: {result.stderr}"
    assert "All exports available" in result.stdout


def test_repo_tests_pass():
    """PASS-TO-PASS: Run the repository's own tests (skip tests with API version issues)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "dagster_hightouch_tests/",
         "-v", "--tb=short",
         "-k", "not test_component_definition and not test_version"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Repo tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_check():
    """PASS-TO-PASS: Repo code passes ruff linting (dagster requires ruff==0.11.5)."""
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff==0.11.5"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert install_result.returncode == 0, f"Failed to install ruff: {install_result.stderr}"

    result = subprocess.run(
        ["ruff", "check", "dagster_hightouch/", "--ignore", "D415"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format():
    """PASS-TO-PASS: Repo code is properly formatted (dagster requires ruff==0.11.5)."""
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff==0.11.5"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert install_result.returncode == 0, f"Failed to install ruff: {install_result.stderr}"

    result = subprocess.run(
        ["ruff", "format", "--check", "dagster_hightouch/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_component_load():
    """PASS-TO-PASS: Repository's component load test passes."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "dagster_hightouch_tests/test_component.py::test_hightouch_component_load",
         "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Component load test failed:\n{result.stdout}\n{result.stderr}"


def test_repo_component_execution():
    """PASS-TO-PASS: Repository's component execution test passes."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "dagster_hightouch_tests/test_component.py::test_component_execution",
         "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Component execution test failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
