"""
Test for dagster_pipes inventory URI fix.
Verifies that transform_inventory_uri correctly handles paths for all packages,
not just those under sections/api/apidocs/dagster/.
"""

import subprocess
import sys
import os
from pathlib import Path

REPO = "/workspace/dagster-io_dagster"


def get_transform_inventory_uri():
    """Extract the transform_inventory_uri function source and return a testable version."""
    # Read the source file
    source_path = os.path.join(REPO, "docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py")
    with open(source_path, "r") as f:
        content = f.read()

    # Extract just the function - find the function definition and extract until the next top-level def
    lines = content.split('\n')
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('def transform_inventory_uri('):
            start_idx = i
            break

    if start_idx is None:
        raise RuntimeError("Could not find transform_inventory_uri function")

    # Extract lines until next top-level def or end of file
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
            if lines[i].startswith('def ') or lines[i].startswith('class '):
                end_idx = i
                break

    func_lines = lines[start_idx:end_idx]
    func_code = '\n'.join(func_lines)

    # Create a namespace to execute the function
    namespace = {}
    exec(func_code, namespace)
    return namespace['transform_inventory_uri']


def test_transform_function_exists():
    """The transform_inventory_uri function exists and can be extracted."""
    transform_inventory_uri = get_transform_inventory_uri()
    assert callable(transform_inventory_uri)


def test_dagster_pipes_uri_transformation():
    """Dagster pipes path should transform from sections/ to root."""
    transform_inventory_uri = get_transform_inventory_uri()

    # dagster_pipes is served at api/dagster/pipes, not under apidocs/
    input_uri = "sections/api/dagster/pipes"
    result = transform_inventory_uri(input_uri)
    assert result == "api/dagster/pipes", f"Expected 'api/dagster/pipes', got '{result}'"


def test_integration_libraries_uri():
    """Integration library paths should strip sections/ prefix."""
    transform_inventory_uri = get_transform_inventory_uri()

    input_uri = "sections/integrations/libraries/dagster-airflow"
    result = transform_inventory_uri(input_uri)
    assert result == "integrations/libraries/dagster-airflow", f"Expected 'integrations/libraries/dagster-airflow', got '{result}'"


def test_trailing_slash_removal():
    """Transformed URIs should have trailing slashes removed."""
    transform_inventory_uri = get_transform_inventory_uri()

    input_uri = "sections/api/dagster/internals/"
    result = transform_inventory_uri(input_uri)
    assert result == "api/dagster/internals", f"Expected 'api/dagster/internals' (no trailing slash), got '{result}'"


def test_non_sections_uri_unchanged():
    """URIs not starting with sections/ should pass through unchanged."""
    transform_inventory_uri = get_transform_inventory_uri()

    input_uri = "api/dagster/pipes"
    result = transform_inventory_uri(input_uri)
    assert result == "api/dagster/pipes", f"Expected unchanged 'api/dagster/pipes', got '{result}'"


def test_sections_only_strips_prefix():
    """Only the sections/ prefix should be stripped, not any other prefix."""
    transform_inventory_uri = get_transform_inventory_uri()

    # Should strip sections/ to get api/dagster/pipes
    input_uri = "sections/api/dagster/pipes"
    result = transform_inventory_uri(input_uri)
    assert result == "api/dagster/pipes"

    # Should strip sections/ to get integrations/libraries/airflow
    input_uri = "sections/integrations/libraries/airflow"
    result = transform_inventory_uri(input_uri)
    assert result == "integrations/libraries/airflow"


def test_repo_ruff_check():
    """Repo's ruff linter passes on dagster-sphinx code (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "--quiet", "ruff==0.15.0"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff formatter passes on dagster-sphinx code (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "--quiet", "ruff==0.15.0"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr[-500:]}"


def test_dagster_sphinx_dir_exists():
    """Sphinx extension directory exists (pass_to_pass smoke test)."""
    assert Path(f"{REPO}/docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py").exists()