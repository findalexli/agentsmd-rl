"""Tests for the dagster_sphinx inventory URI fix.

This tests that the transform_inventory_uri function correctly transforms
Sphinx source paths to final documentation URLs.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/dagster")
TARGET_FILE = REPO / "docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py"


def import_transform_function():
    """Import and return the transform_inventory_uri function."""
    # Add the dagster_sphinx path to sys.path
    sphinx_ext_path = str(REPO / "docs/sphinx/_ext/dagster-sphinx")
    if sphinx_ext_path not in sys.path:
        sys.path.insert(0, sphinx_ext_path)

    # Also need dagster package for imports
    dagster_path = str(REPO / "python_modules/dagster")
    if dagster_path not in sys.path:
        sys.path.insert(0, dagster_path)

    from dagster_sphinx import transform_inventory_uri
    return transform_inventory_uri


def test_transform_api_apidocs_prefix():
    """Test that sections/api/apidocs/ is transformed to api/."""
    transform = import_transform_function()

    # Main case from the PR - the fix transforms this correctly
    result = transform("sections/api/apidocs/dagster/internals/")
    assert result == "api/dagster/internals", f"Expected 'api/dagster/internals', got '{result}'"


def test_transform_api_apidocs_no_trailing_slash():
    """Test transformation without trailing slash."""
    transform = import_transform_function()

    result = transform("sections/api/apidocs/dagster/pipes")
    assert result == "api/dagster/pipes", f"Expected 'api/dagster/pipes', got '{result}'"


def test_transform_api_apidocs_root():
    """Test transformation of the root apidocs path."""
    transform = import_transform_function()

    result = transform("sections/api/apidocs/")
    assert result == "api", f"Expected 'api', got '{result}'"


def test_no_transform_other_paths():
    """Test that paths without the prefix are not modified."""
    transform = import_transform_function()

    # Paths that don't start with sections/api/apidocs/ should be unchanged
    result = transform("other/path/to/docs")
    assert result == "other/path/to/docs", f"Expected 'other/path/to/docs', got '{result}'"

    result = transform("integrations/libraries/some-lib")
    assert result == "integrations/libraries/some-lib", f"Expected unchanged, got '{result}'"


def test_ruff_formatting():
    """Test that the code passes ruff formatting and linting."""
    # Run ruff check on the target file
    result = subprocess.run(
        ["python", "-m", "ruff", "check", str(TARGET_FILE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_format():
    """Test that the code is properly formatted according to ruff."""
    # Run ruff format check (dry-run)
    result = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", str(TARGET_FILE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_dagster_sphinx_imports():
    """Test that dagster_sphinx module and its exports can be imported (pass_to_pass)."""
    # Add the dagster_sphinx path to sys.path
    sphinx_ext_path = str(REPO / "docs/sphinx/_ext/dagster-sphinx")
    if sphinx_ext_path not in sys.path:
        sys.path.insert(0, sphinx_ext_path)

    # Also need dagster package for imports
    dagster_path = str(REPO / "python_modules/dagster")
    if dagster_path not in sys.path:
        sys.path.insert(0, dagster_path)

    # Test importing the main module and key functions
    from dagster_sphinx import transform_inventory_uri, DagsterClassDocumenter, process_docstring
    from dagster_sphinx.configurable import ConfigurableDocumenter
    from dagster_sphinx.docstring_flags import FlagDirective

    # Verify key functions are callable
    assert callable(transform_inventory_uri)
    assert callable(process_docstring)


def test_python_syntax():
    """Test that the target file has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "py_compile", str(TARGET_FILE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Python syntax check failed:\n{result.stderr}"
