"""Test outputs for Gradio task.

This module contains:
1. fail_to_pass tests: Tests that fail before the fix and pass after
2. pass_to_pass tests: Tests that should always pass (enriched with repo CI tests)
"""

import subprocess
import sys
from pathlib import Path

import pytest

# REPO path inside the Docker container - must match Dockerfile WORKDIR
REPO = "/workspace/gradio"


def test_fail_to_pass_docstring_added():
    """The get_interface_ip function should have a proper docstring (fail_to_pass)."""
    # First check the function exists
    result = subprocess.run(
        ["python", "-c", f"import gradio.utils; assert hasattr(gradio.utils, 'get_interface_ip'), 'get_interface_ip function not found'"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    if result.returncode != 0:
        pytest.fail(f"get_interface_ip function does not exist: {result.stderr}")

    # Then check it has a docstring
    result = subprocess.run(
        ["python", "-c", f"import gradio.utils; assert gradio.utils.get_interface_ip.__doc__ is not None, 'Function has no docstring'"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Function should have a docstring: {result.stderr}"


# =============================================================================
# Pass-to-Pass Tests - Enriched with actual repo CI commands
# =============================================================================

def test_repo_imports():
    """Gradio package can be imported without errors (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "import gradio; print('Gradio imported successfully')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Import failed:\n{result.stderr}"


def test_repo_client_imports():
    """Gradio client package can be imported without errors (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from gradio_client import Client; print('Client imported successfully')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Client import failed:\n{result.stderr}"


def test_repo_ruff_check_gradio():
    """Repo's gradio source has no critical errors (pass_to_pass).

    Source: .github/workflows/test-python.yml -> scripts/lint_backend.sh
    We check for syntax errors (E9), indentation errors (E1), and
    import/fatal issues (F) which would actually break code execution.
    Line length (E501) and style issues are excluded as they are
    pre-existing in the codebase and configured to be ignored.
    """
    # Check only for critical issues that would break code
    result = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/", "--select", "E9,E1,F"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff found critical errors:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_gradio_cli_works():
    """Gradio CLI is installed and accessible (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "gradio", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Gradio CLI failed:\n{result.stderr}"
    assert "usage" in result.stdout.lower(), f"Expected usage info, got: {result.stdout}"


def test_repo_gradio_version():
    """Gradio has a valid version string (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "import gradio; print(gradio.__version__)"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Failed to get version:\n{result.stderr}"
    version = result.stdout.strip()
    assert version, f"Version is empty"
    # Check version format (should be like 5.x.x)
    parts = version.split(".")
    assert len(parts) >= 2, f"Invalid version format: {version}"


def test_repo_client_version():
    """Gradio client has a valid version string (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from gradio_client import __version__; print(__version__)"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Failed to get client version:\n{result.stderr}"
    version = result.stdout.strip()
    assert version, f"Client version is empty"


def test_repo_pyi_files_generated():
    """Gradio .pyi stub files are generated (pass_to_pass).

    This is checked in CI via the 'Generate .pyi files' step.
    """
    # Import gradio which triggers .pyi generation
    result = subprocess.run(
        ["python", "-c", "import gradio; print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Failed to import gradio:\n{result.stderr}"

    # Check that at least one .pyi file exists
    result = subprocess.run(
        ["python", "-c", "from pathlib import Path; files = list(Path('gradio').glob('*.pyi')); assert len(files) > 0, 'No .pyi files found'; print(f'Found {len(files)} .pyi files')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f".pyi check failed:\n{result.stderr}"


def test_repo_package_structure():
    """Gradio package has expected top-level structure (pass_to_pass)."""
    expected_modules = [
        "gradio.components",
        "gradio.themes",
        "gradio.events",
        "gradio.routes",
    ]
    for module in expected_modules:
        result = subprocess.run(
            ["python", "-c", f"import {module}; print('OK')"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed to import {module}:\n{result.stderr}"


def test_repo_ruff_format_check():
    """Repo's Python code passes ruff format check (pass_to_pass).

    Source: .github/workflows/test-python.yml -> scripts/lint_backend.sh
    This checks that Python code is properly formatted.
    """
    # Check only gradio/utils.py for formatting (the file modified by this task)
    result = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/utils.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_test_analytics():
    """Repo's analytics tests pass (pass_to_pass).

    Source: test/test_analytics.py - simple, fast tests that don't require
    network or additional dependencies like hypothesis.
    """
    result = subprocess.run(
        ["python", "-m", "pytest", "test/test_analytics.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Analytics tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_test_http_server():
    """Repo's HTTP server tests pass (pass_to_pass).

    Source: test/test_http_server.py - tests basic server functionality
    without requiring complex setup or network access.
    """
    result = subprocess.run(
        ["python", "-m", "pytest", "test/test_http_server.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"HTTP server tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_import_gradio_utils():
    """Gradio utils module imports correctly (pass_to_pass).

    Relevant to the task which modifies gradio/utils.py.
    Verifies the modified module can be imported without errors.
    """
    result = subprocess.run(
        ["python", "-c", "from gradio import utils; print('gradio.utils imported successfully')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"gradio.utils import failed:\n{result.stderr}"


def test_repo_utils_functions_exist():
    """Key gradio.utils functions are accessible (pass_to_pass).

    Verifies that expected utility functions from gradio.utils exist
    and are callable after the fix.
    """
    # Check some common utility functions that should exist in gradio.utils
    check_code = """
from gradio.utils import (
    get_function_description,
    get_function_params,
    delete_none,
    diff,
    validate_url,
    safe_deepcopy,
)
print("All expected utils functions are accessible")
"""
    result = subprocess.run(
        ["python", "-c", check_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Utils functions check failed:\n{result.stderr}"


# =============================================================================
# NEW Pass-to-Pass Tests - CI/CD Enrichment
# =============================================================================

def test_repo_ruff_format_check_utils():
    """Repo's gradio/utils.py passes ruff format check (pass_to_pass).

    Source: .github/workflows/test-python.yml -> scripts/lint_backend.sh
    The modified file must be properly formatted.
    """
    result = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/utils.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_client_utils_tests():
    """Gradio client utils tests pass (pass_to_pass).

    Source: client/python/test/test_utils.py
    Tests the gradio_client utilities that complement gradio.utils.
    These are fast, isolated unit tests (87 tests).
    """
    # Install test dependencies first
    subprocess.run(
        ["pip", "install", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # Run the client utils tests
    result = subprocess.run(
        ["python", "-m", "pytest", "client/python/test/test_utils.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Client utils tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_test_image_utils():
    """Gradio image utils tests pass (pass_to_pass).

    Source: test/test_image_utils.py
    Tests image utility functions. Fast tests with minimal dependencies.
    """
    result = subprocess.run(
        ["python", "-m", "pytest", "test/test_image_utils.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Image utils tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_test_processing_utils_subset():
    """Gradio processing utils core tests pass (pass_to_pass).

    Source: test/test_processing_utils.py - selected fast, reliable tests
    Tests file processing utilities without heavy dependencies.
    """
    # Install hypothesis for parameterized tests
    subprocess.run(
        ["pip", "install", "hypothesis", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # Run a subset of processing utils tests that don't need matplotlib/ffmpeg
    result = subprocess.run(
        ["python", "-m", "pytest",
         "test/test_processing_utils.py::TestTempFileManagement",
         "test/test_processing_utils.py::TestMoveFilesToCacheSecurity",
         "test/test_processing_utils.py::TestAudioFormatDetection",
         "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Processing utils tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


if __name__ == "__main__":
    # Simple test runner for manual execution
    import traceback

    tests = [
        test_repo_imports,
        test_repo_client_imports,
        test_repo_ruff_check_gradio,
        test_repo_gradio_cli_works,
        test_repo_gradio_version,
        test_repo_client_version,
        test_repo_pyi_files_generated,
        test_repo_package_structure,
        test_repo_ruff_format_check,
        test_repo_test_analytics,
        test_repo_test_http_server,
        test_repo_import_gradio_utils,
        test_repo_utils_functions_exist,
        test_repo_ruff_format_check_utils,
        test_repo_client_utils_tests,
        test_repo_test_image_utils,
        test_repo_test_processing_utils_subset,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {traceback.format_exc()}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
