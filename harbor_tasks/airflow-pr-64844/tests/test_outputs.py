#!/usr/bin/env python3
"""
Tests for the cooldown parameter feature in constraints-version-check.

These tests verify that:
1. The get_latest_version_with_cooldown function exists and works correctly
2. It filters out versions released within the cooldown period
3. It returns the latest qualifying version outside the cooldown
4. Edge cases are handled properly (no qualifying versions, empty releases, etc.)
"""

import ast
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Path to the target file
REPO = Path("/workspace/airflow")
TARGET_FILE = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "utils" / "constraints_version_check.py"


def extract_function_from_source(source_code: str, function_name: str) -> str | None:
    """Extract a specific function's source code from a module."""
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Get line numbers
            start = node.lineno - 1
            end = node.end_lineno
            lines = source_code.split('\n')
            return '\n'.join(lines[start:end])
    return None


def get_function_from_file(func_name: str):
    """Load a function from the target file dynamically, avoiding problematic imports."""
    source = TARGET_FILE.read_text()

    # Create a minimal namespace with required imports
    namespace = {
        'datetime': datetime,
        'timedelta': timedelta,
        'Any': object,
        '__name__': '__main__',
    }

    # Extract just the function we need plus any required helper code
    func_source = extract_function_from_source(source, func_name)
    if func_source is None:
        return None

    # Add necessary imports
    preamble = """
from datetime import datetime, timedelta
from typing import Any
from packaging import version
"""

    try:
        exec(preamble + "\n" + func_source, namespace)
        return namespace.get(func_name)
    except Exception:
        return None


def test_get_latest_version_with_cooldown_exists():
    """Test that the get_latest_version_with_cooldown function exists (fail_to_pass)."""
    source = TARGET_FILE.read_text()
    assert "def get_latest_version_with_cooldown(" in source, \
        "get_latest_version_with_cooldown function should be defined"


def test_cooldown_function_has_correct_signature():
    """Test that the cooldown function has the correct signature (fail_to_pass)."""
    source = TARGET_FILE.read_text()
    # Check for function with cooldown_days parameter
    assert "def get_latest_version_with_cooldown(releases:" in source and "cooldown_days:" in source, \
        "get_latest_version_with_cooldown should have releases and cooldown_days parameters"


def test_cooldown_filters_recent_versions():
    """Test that cooldown filtering excludes versions released within the cooldown period (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist and be importable"

    now = datetime.now()

    # Create mock releases: one recent (within cooldown), one older (outside cooldown)
    releases = {
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=10)).isoformat() + "Z"}],
        "2.0.0": [{"upload_time_iso_8601": (now - timedelta(days=1)).isoformat() + "Z"}],  # Within 4-day cooldown
    }

    result = func(releases, cooldown_days=4)

    # Should return 1.0.0 since 2.0.0 is too recent
    assert result == "1.0.0", f"Expected 1.0.0, got {result}"


def test_cooldown_returns_latest_outside_cooldown():
    """Test that cooldown returns the latest version outside the cooldown period (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    # All versions are outside the cooldown period
    releases = {
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=30)).isoformat() + "Z"}],
        "1.5.0": [{"upload_time_iso_8601": (now - timedelta(days=20)).isoformat() + "Z"}],
        "2.0.0": [{"upload_time_iso_8601": (now - timedelta(days=10)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return 2.0.0 since it's the latest and outside cooldown
    assert result == "2.0.0", f"Expected 2.0.0, got {result}"


def test_cooldown_returns_none_when_all_recent():
    """Test that cooldown returns None when all versions are within the cooldown period (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    # All versions are within the cooldown period
    releases = {
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=1)).isoformat() + "Z"}],
        "2.0.0": [{"upload_time_iso_8601": (now - timedelta(days=2)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return None since all versions are too recent
    assert result is None, f"Expected None, got {result}"


def test_cooldown_skips_prerelease_versions():
    """Test that cooldown filtering skips pre-release versions (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    # Mix of prerelease and stable versions
    releases = {
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=30)).isoformat() + "Z"}],
        "2.0.0a1": [{"upload_time_iso_8601": (now - timedelta(days=20)).isoformat() + "Z"}],  # Prerelease
        "2.0.0rc1": [{"upload_time_iso_8601": (now - timedelta(days=15)).isoformat() + "Z"}],  # Prerelease
        "1.5.0": [{"upload_time_iso_8601": (now - timedelta(days=10)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return 1.5.0 (latest stable), not prerelease versions
    assert result == "1.5.0", f"Expected 1.5.0, got {result}"


def test_cooldown_skips_dev_versions():
    """Test that cooldown filtering skips dev versions (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    releases = {
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=30)).isoformat() + "Z"}],
        "2.0.0.dev1": [{"upload_time_iso_8601": (now - timedelta(days=20)).isoformat() + "Z"}],  # Dev release
        "1.5.0": [{"upload_time_iso_8601": (now - timedelta(days=10)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return 1.5.0 (latest stable), not dev version
    assert result == "1.5.0", f"Expected 1.5.0, got {result}"


def test_cooldown_handles_empty_releases():
    """Test that cooldown handles empty release data gracefully (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    releases = {
        "1.0.0": [],  # Empty release data
        "2.0.0": [{"upload_time_iso_8601": (now - timedelta(days=10)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return 2.0.0, skipping the empty release
    assert result == "2.0.0", f"Expected 2.0.0, got {result}"


def test_cooldown_with_custom_days():
    """Test cooldown with different cooldown_days values (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    releases = {
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=30)).isoformat() + "Z"}],
        "2.0.0": [{"upload_time_iso_8601": (now - timedelta(days=8)).isoformat() + "Z"}],
    }

    # With 10-day cooldown, 2.0.0 should be excluded
    result_10 = func(releases, cooldown_days=10)
    assert result_10 == "1.0.0", f"With 10-day cooldown: Expected 1.0.0, got {result_10}"

    # With 5-day cooldown, 2.0.0 should be included
    result_5 = func(releases, cooldown_days=5)
    assert result_5 == "2.0.0", f"With 5-day cooldown: Expected 2.0.0, got {result_5}"


def test_constraints_version_check_has_cooldown_parameter():
    """Test that constraints_version_check function accepts cooldown_days parameter (fail_to_pass)."""
    source = TARGET_FILE.read_text()

    # Find the function definition and check for cooldown_days parameter
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "constraints_version_check":
            param_names = [arg.arg for arg in node.args.args] + [arg.arg for arg in node.args.kwonlyargs]
            assert "cooldown_days" in param_names, \
                f"constraints_version_check should have cooldown_days parameter. Found: {param_names}"
            return

    assert False, "constraints_version_check function not found"


def test_process_packages_has_cooldown_parameter():
    """Test that process_packages function accepts cooldown_days parameter (fail_to_pass)."""
    source = TARGET_FILE.read_text()

    # Find the function definition and check for cooldown_days parameter
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "process_packages":
            param_names = [arg.arg for arg in node.args.args] + [arg.arg for arg in node.args.kwonlyargs]
            assert "cooldown_days" in param_names, \
                f"process_packages should have cooldown_days parameter. Found: {param_names}"
            return

    assert False, "process_packages function not found"


def test_timedelta_imported():
    """Test that timedelta is imported in the module (fail_to_pass)."""
    source = TARGET_FILE.read_text()
    assert "from datetime import datetime, timedelta" in source or \
           ("from datetime import" in source and "timedelta" in source), \
        "timedelta should be imported from datetime"


def test_cooldown_handles_invalid_versions():
    """Test that cooldown handles invalid version strings gracefully (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    releases = {
        "invalid-version": [{"upload_time_iso_8601": (now - timedelta(days=30)).isoformat() + "Z"}],
        "1.0.0": [{"upload_time_iso_8601": (now - timedelta(days=20)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return 1.0.0, skipping the invalid version
    assert result == "1.0.0", f"Expected 1.0.0, got {result}"


def test_cooldown_handles_missing_upload_time():
    """Test that cooldown handles missing upload_time_iso_8601 gracefully (fail_to_pass)."""
    func = get_function_from_file("get_latest_version_with_cooldown")
    assert func is not None, "get_latest_version_with_cooldown function should exist"

    now = datetime.now()

    releases = {
        "1.0.0": [{"other_field": "value"}],  # Missing upload_time_iso_8601
        "2.0.0": [{"upload_time_iso_8601": (now - timedelta(days=10)).isoformat() + "Z"}],
    }

    result = func(releases, cooldown_days=4)

    # Should return 2.0.0, skipping the release with missing time
    assert result == "2.0.0", f"Expected 2.0.0, got {result}"


# Pass-to-pass tests - these should pass both before and after the fix

def test_is_valid_version_exists():
    """Test that is_valid_version function exists (pass_to_pass)."""
    source = TARGET_FILE.read_text()
    assert "def is_valid_version(" in source, "is_valid_version function should exist"


def test_count_versions_between_exists():
    """Test that count_versions_between function exists (pass_to_pass)."""
    source = TARGET_FILE.read_text()
    assert "def count_versions_between(" in source, "count_versions_between function should exist"


def test_parse_constraints_generation_date_exists():
    """Test that parse_constraints_generation_date function exists (pass_to_pass)."""
    source = TARGET_FILE.read_text()
    assert "def parse_constraints_generation_date(" in source, "parse_constraints_generation_date function should exist"


def test_file_exists():
    """Test that the target file exists (pass_to_pass)."""
    assert TARGET_FILE.exists(), f"Target file should exist: {TARGET_FILE}"


# Subprocess-based pass-to-pass tests that run actual CI commands

import subprocess


def test_repo_python_syntax():
    """Python syntax check passes for constraints_version_check.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"


def test_repo_ast_parse():
    """AST parsing succeeds for constraints_version_check.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", f"import ast; ast.parse(open('{TARGET_FILE}').read())"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"


def test_repo_breeze_utils_syntax():
    """Python syntax check passes for all utils in breeze utils directory (pass_to_pass)."""
    utils_dir = REPO / "dev" / "breeze" / "src" / "airflow_breeze" / "utils"
    r = subprocess.run(
        ["python", "-m", "py_compile"] + [str(f) for f in utils_dir.glob("*.py")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed for utils:\n{r.stderr[-500:]}"
