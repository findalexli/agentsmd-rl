"""Tests for appwrite-variable-id-optional task.

Verifies that the createProjectVariable endpoint correctly makes variableId optional
with a default value of 'unique()' to match other variable creation endpoints.
"""

import subprocess
import re
import os
import pytest

REPO = "/workspace/appwrite"
TARGET_FILE = f"{REPO}/src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php"


def php_syntax_valid():
    """Check if PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", TARGET_FILE],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def test_php_syntax_valid():
    """Verify the modified PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", TARGET_FILE],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_param_optional_with_unique_default():
    """Verify variableId param is optional (5th param is true) with 'unique()' default."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the param line for variableId
    # Looking for: ->param('variableId', 'unique()', ..., ..., true, ...)
    # The 2nd argument is default, 5th argument is optional flag
    param_pattern = r"->param\(\s*'variableId'\s*,\s*'unique\(\)'\s*,[^,]+,\s*'Variable ID\.[^']*'\s*,\s*true"

    match = re.search(param_pattern, content)
    assert match is not None, (
        "variableId param must be optional with default 'unique()'\n"
        "Expected: ->param('variableId', 'unique()', ..., ..., true, ...)\n"
        "The 5th parameter should be 'true' to make it optional."
    )


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_matches_function_and_sites_behavior():
    """Verify the fix matches patterns used in Functions and Sites variable endpoints."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Extract the entire param call
    param_match = re.search(
        r"->param\('variableId'\s*,\s*'unique\(\)'\s*,\s*fn\s*\([^)]+\)\s*=>\s*new\s+CustomId",
        content
    )
    assert param_match is not None, (
        "variableId param should use 'unique()' default with CustomId validator.\n"
        "This matches the behavior of Functions and Sites variable endpoints."
    )


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_param_not_required():
    """Verify variableId param is explicitly marked as optional (required=false means mandatory)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # In the param() call, the 5th argument controls whether param is optional:
    # ->param(name, default, validator, description, optional, injects)
    # optional=true means the param is NOT required
    # We need to ensure the param is marked as optional=true

    # Find the complete param call
    param_match = re.search(
        r"->param\(\s*'variableId'\s*,\s*'unique\(\)'\s*,\s*fn\s*\([^)]+\)\s*=>\s*new\s+CustomId\([^)]+\)\s*,\s*'Variable ID\.[^']+'\s*,\s*(true|false)",
        content,
        re.DOTALL
    )

    assert param_match is not None, (
        "Could not find variableId param definition with expected structure.\n"
        "Expected pattern: ->param('variableId', 'unique()', fn (...) => new CustomId(...), '...', true, ...)"
    )

    optional_flag = param_match.group(1)
    assert optional_flag == "true", (
        f"variableId param must be optional (5th argument should be 'true', got '{optional_flag}').\n"
        "The optional flag must be true to allow requests without variableId."
    )
