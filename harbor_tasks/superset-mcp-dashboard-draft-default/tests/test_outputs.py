"""
Tests for superset-mcp-dashboard-draft-default task.

This verifies that dashboards created via MCP default to draft (published=False)
rather than being published by default.
"""

import ast
import sys
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
SCHEMAS_FILE = REPO / "superset/mcp_service/dashboard/schemas.py"


# =============================================================================
# PASS-TO-PASS: Repo CI/CD Checks
# These tests verify that the repo's own CI/CD checks pass on the base commit.
# =============================================================================


def test_repo_ruff_check():
    """
    PASS-TO-PASS: Repo code passes ruff linting checks.

    This ensures the code follows the repo's linting standards.
    """
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "check", str(SCHEMAS_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """
    PASS-TO-PASS: Repo code passes ruff formatting checks.

    This ensures the code follows the repo's formatting standards.
    """
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", str(SCHEMAS_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax():
    """
    PASS-TO-PASS: Repo Python files have valid syntax.

    This validates that the schemas file can be parsed by the Python AST parser.
    """
    content = SCHEMAS_FILE.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Python syntax error in {SCHEMAS_FILE}: {e}")


def test_schemas_file_exists():
    """Verify the schemas.py file exists in the repository."""
    assert SCHEMAS_FILE.exists(), f"Schemas file not found at {SCHEMAS_FILE}"


def test_published_defaults_to_false():
    """
    FAIL-TO-PASS: Verify that GenerateDashboardRequest.published defaults to False.

    This is the primary behavioral test. On the buggy base commit, this will fail
    because published defaults to True. After the fix, it should pass.
    """
    # Read the file content
    content = SCHEMAS_FILE.read_text()

    # Find the GenerateDashboardRequest class and its published field
    lines = content.split('\n')
    in_class = False
    found_field_line = None
    default_value = None

    for i, line in enumerate(lines):
        if 'class GenerateDashboardRequest' in line:
            in_class = True
        elif in_class and 'published: bool = Field(' in line:
            # Look at the next line(s) for the default value
            for j in range(i + 1, min(i + 3, len(lines))):
                if 'default=' in lines[j]:
                    found_field_line = j
                    # Extract the default value
                    if 'default=True' in lines[j]:
                        default_value = True
                    elif 'default=False' in lines[j]:
                        default_value = False
                    break
            break

    assert found_field_line is not None, "Could not find published field with default in GenerateDashboardRequest"
    assert default_value is not None, "Could not determine default value for published field"
    assert default_value is False, f"published should default to False, but found default={default_value}"


def test_published_field_description():
    """
    PASS-TO-PASS: Verify the published field has the correct description.

    This tests that the field description mentions publishing/publish.
    """
    content = SCHEMAS_FILE.read_text()

    # Find the published field and verify description mentions publishing
    assert 'published: bool = Field(' in content, "published field declaration not found"

    # The description should mention publishing
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'published: bool = Field(' in line:
            # Check next few lines for description
            field_block = '\n'.join(lines[i:i+3])
            assert 'description="Whether to publish the dashboard"' in field_block or \
                   'description="' in field_block and 'publish' in field_block.lower(), \
                "published field should have a description mentioning publishing"
            break


def test_generate_dashboard_request_class_exists():
    """
    PASS-TO-PASS: Verify the GenerateDashboardRequest class exists.

    This is a structural check gated behind the behavioral test.
    """
    content = SCHEMAS_FILE.read_text()
    assert 'class GenerateDashboardRequest(BaseModel):' in content, \
        "GenerateDashboardRequest class not found"


def test_imports_pydantic_base_model():
    """
    PASS-TO-PASS: Verify the file properly imports Pydantic BaseModel.
    """
    content = SCHEMAS_FILE.read_text()
    assert 'from pydantic import' in content and 'BaseModel' in content, \
        "File should import BaseModel from pydantic"


def test_no_default_true_in_published_field():
    """
    FAIL-TO-PASS: Verify that the published field does NOT default to True.

    This test specifically checks for the bug pattern.
    """
    content = SCHEMAS_FILE.read_text()

    # Look for the published field definition in GenerateDashboardRequest
    lines = content.split('\n')
    in_generate_class = False

    for i, line in enumerate(lines):
        if 'class GenerateDashboardRequest' in line:
            in_generate_class = True
        elif in_generate_class and line.strip().startswith('class ') and 'GenerateDashboardRequest' not in line:
            # We've moved to another class
            break
        elif in_generate_class and 'published' in line and 'default=True' in line:
            pytest.fail(f"BUG: published field defaults to True at line {i+1}: {line.strip()}")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
