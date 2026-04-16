"""
Test outputs for apache/superset PR #39207

This PR fixes a bug where Jinja templates in virtual dataset SQL were not being
rendered when used with cross-filters (adhoc filter columns). The fix ensures
template_processor is passed to adhoc_column_to_sqla so Jinja templates get
rendered before SQLGlot parses the SQL.
"""

import ast
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")
HELPERS_FILE = REPO / "superset" / "models" / "helpers.py"


# =============================================================================
# Fail-to-pass tests: These should FAIL on base commit, PASS after fix
# =============================================================================


def test_adhoc_column_filter_passes_template_processor():
    """
    Verify that adhoc_column_to_sqla is called with template_processor when
    processing adhoc column filters in get_sqla_query.

    The bug was that the call at line ~3012 did NOT pass template_processor,
    causing Jinja templates like {{ current_username() }} to fail parsing.

    This test verifies the fix by checking that template_processor is passed
    to adhoc_column_to_sqla when processing adhoc column filters.
    """
    # Read the helpers.py file
    content = HELPERS_FILE.read_text()

    # Find the specific section where adhoc column filters are processed
    # We're looking for the is_adhoc_column(flt_col) block in the filter loop

    # The pattern we need to find: after "elif is_adhoc_column(flt_col):"
    # there should be a call to adhoc_column_to_sqla that includes
    # template_processor=template_processor

    # Find the filter processing section
    pattern = r"elif is_adhoc_column\(flt_col\):.*?(?=elif|else:|\n\s{12}(?![ ])|$)"
    matches = re.findall(pattern, content, re.DOTALL)

    # There should be at least one match for filter processing
    assert matches, "Could not find adhoc column filter processing section"

    # Check each match to see if it contains template_processor parameter
    found_filter_section = False
    has_template_processor = False

    for match in matches:
        # This is the filter processing section (contains applied_adhoc_filters_columns)
        if "applied_adhoc_filters_columns" in match:
            found_filter_section = True
            # Check if template_processor is passed to adhoc_column_to_sqla
            if "template_processor=template_processor" in match:
                has_template_processor = True
                break

    assert found_filter_section, "Could not find the adhoc filter processing section"
    assert has_template_processor, (
        "adhoc_column_to_sqla call in filter processing does not include "
        "template_processor parameter - Jinja templates won't be rendered"
    )


def test_adhoc_column_filter_template_processor_in_call():
    """
    Test that adhoc_column_to_sqla call for filters includes template_processor.

    Uses AST parsing to verify the function call has the correct keyword argument.
    """
    content = HELPERS_FILE.read_text()

    # Parse the file as AST
    tree = ast.parse(content)

    # Find the get_sqla_query method
    get_sqla_query_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_sqla_query":
            get_sqla_query_func = node
            break

    assert get_sqla_query_func is not None, "Could not find get_sqla_query function"

    # Find all calls to adhoc_column_to_sqla within the function
    adhoc_column_calls = []
    for node in ast.walk(get_sqla_query_func):
        if isinstance(node, ast.Call):
            # Check if this is a call to adhoc_column_to_sqla (method call)
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "adhoc_column_to_sqla":
                    adhoc_column_calls.append(node)

    assert adhoc_column_calls, "No calls to adhoc_column_to_sqla found in get_sqla_query"

    # Check that ALL calls have template_processor parameter
    # The fix is specifically for the filter processing section
    for call in adhoc_column_calls:
        keywords = {kw.arg for kw in call.keywords if kw.arg is not None}
        # Skip calls that don't have force_type_check (not the filter section)
        if "force_type_check" in keywords:
            assert "template_processor" in keywords, (
                f"adhoc_column_to_sqla call at line {call.lineno} with force_type_check "
                "does not have template_processor parameter"
            )


def test_jinja_template_in_adhoc_filter_would_be_processed():
    """
    Verify the template_processor parameter flow for adhoc column filters.

    This test ensures the code path processes templates by checking that:
    1. adhoc_column_to_sqla accepts template_processor
    2. The filter processing code passes it through
    """
    content = HELPERS_FILE.read_text()

    # Find all occurrences of adhoc_column_to_sqla with force_type_check=True
    # (this is the filter processing path)
    pattern = r"adhoc_column_to_sqla\([^)]*force_type_check\s*=\s*True[^)]*\)"
    matches = re.findall(pattern, content, re.DOTALL)

    assert matches, "Could not find adhoc_column_to_sqla call with force_type_check=True"

    # Each such call should also have template_processor
    for match in matches:
        assert "template_processor" in match, (
            f"adhoc_column_to_sqla call with force_type_check=True "
            f"is missing template_processor: {match}"
        )


# =============================================================================
# Pass-to-pass tests: These should PASS both before and after the fix
# =============================================================================


def test_python_syntax_valid():
    """Verify that helpers.py has valid Python syntax."""
    content = HELPERS_FILE.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in helpers.py: {e}")


def test_adhoc_column_to_sqla_accepts_template_processor():
    """
    Verify that adhoc_column_to_sqla method signature accepts template_processor.

    This is a prerequisite for the fix - the method must accept the parameter.
    """
    content = HELPERS_FILE.read_text()

    # Parse the file
    tree = ast.parse(content)

    # Find the adhoc_column_to_sqla method(s)
    found_method = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "adhoc_column_to_sqla":
            found_method = True
            # Get parameter names
            param_names = [arg.arg for arg in node.args.args]
            assert "template_processor" in param_names, (
                "adhoc_column_to_sqla does not have template_processor parameter"
            )

    assert found_method, "Could not find adhoc_column_to_sqla method"


def test_get_sqla_query_exists():
    """Verify that get_sqla_query method exists in helpers.py."""
    content = HELPERS_FILE.read_text()
    tree = ast.parse(content)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_sqla_query":
            found = True
            break

    assert found, "get_sqla_query method not found in helpers.py"


def test_imports_are_valid():
    """Verify key imports exist in helpers.py."""
    content = HELPERS_FILE.read_text()

    # Check for key imports used in template processing
    assert "BaseTemplateProcessor" in content, (
        "BaseTemplateProcessor not imported"
    )
    assert "is_adhoc_column" in content, (
        "is_adhoc_column not imported/defined"
    )


def test_other_adhoc_column_calls_have_template_processor():
    """
    Verify that other adhoc_column_to_sqla calls (outside filter section)
    already pass template_processor.

    The PR description mentions lines 2829 and 2880 already passed it correctly.
    This confirms those existing patterns.
    """
    content = HELPERS_FILE.read_text()
    tree = ast.parse(content)

    # Find get_sqla_query function
    get_sqla_query_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_sqla_query":
            get_sqla_query_func = node
            break

    assert get_sqla_query_func is not None

    # Count calls with and without template_processor
    calls_with_tp = 0
    calls_without_tp = 0

    for node in ast.walk(get_sqla_query_func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "adhoc_column_to_sqla":
                    keywords = {kw.arg for kw in node.keywords if kw.arg is not None}
                    if "template_processor" in keywords:
                        calls_with_tp += 1
                    else:
                        calls_without_tp += 1

    # After the fix, all calls should have template_processor
    # Before the fix, at least some calls should have it
    assert calls_with_tp >= 1, (
        "Expected at least some adhoc_column_to_sqla calls to have template_processor"
    )


# =============================================================================
# Pass-to-pass tests: Real CI commands via subprocess (pass_to_pass / repo_tests)
# =============================================================================


@pytest.fixture(scope="module")
def ensure_ruff():
    """Install ruff if not available."""
    result = subprocess.run(
        ["pip", "install", "ruff==0.11.4", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Don't fail if already installed
    return result.returncode == 0


def test_repo_ruff_lint_helpers(ensure_ruff):
    """Repo's ruff linter passes on helpers.py (pass_to_pass)."""
    result = subprocess.run(
        [
            "ruff",
            "check",
            "superset/models/helpers.py",
            "--select=E,F,W",
            "--ignore=E501",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_lint_models(ensure_ruff):
    """Repo's ruff linter passes on models directory (pass_to_pass)."""
    result = subprocess.run(
        [
            "ruff",
            "check",
            "superset/models/",
            "--select=E,F,W",
            "--ignore=E501",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format_helpers(ensure_ruff):
    """Repo's ruff format check passes on helpers.py (pass_to_pass)."""
    result = subprocess.run(
        ["ruff", "format", "--check", "superset/models/helpers.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Ruff format failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_isort_helpers(ensure_ruff):
    """Repo's import sorting check passes on helpers.py (pass_to_pass)."""
    result = subprocess.run(
        ["ruff", "check", "superset/models/helpers.py", "--select=I"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Ruff isort failed:\n{result.stdout}\n{result.stderr}"


def test_repo_python_compile_helpers():
    """Python compilation check passes on helpers.py (pass_to_pass)."""
    result = subprocess.run(
        ["python", "-m", "py_compile", "superset/models/helpers.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Python compile failed:\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
