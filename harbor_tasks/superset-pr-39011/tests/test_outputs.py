"""
Tests for superset-mcp-dashboard-draft task.

This task verifies that the GenerateDashboardRequest schema defaults
the 'published' field to False (draft state) rather than True.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/superset")
SCHEMA_FILE = REPO / "superset" / "mcp_service" / "dashboard" / "schemas.py"


def test_published_default_is_false():
    """
    GenerateDashboardRequest.published should default to False.

    When creating dashboards through MCP, they should be in draft state
    by default, consistent with manual dashboard creation.

    Type: fail_to_pass
    """
    source = SCHEMA_FILE.read_text()
    tree = ast.parse(source)

    # Find the GenerateDashboardRequest class
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GenerateDashboardRequest":
            class_node = node
            break

    assert class_node is not None, "GenerateDashboardRequest class not found in schemas.py"

    # Find the 'published' field assignment
    published_field = None
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            if stmt.target.id == "published":
                published_field = stmt
                break

    assert published_field is not None, "published field not found in GenerateDashboardRequest"

    # The value should be a Call to Field()
    assert isinstance(published_field.value, ast.Call), "published field should use Field()"

    # Find the 'default' keyword argument
    default_value = None
    for keyword in published_field.value.keywords:
        if keyword.arg == "default":
            default_value = keyword.value
            break

    assert default_value is not None, "published field should have a default keyword"

    # Check the default is False (not True)
    if isinstance(default_value, ast.Constant):
        actual_default = default_value.value
    elif isinstance(default_value, ast.NameConstant):  # Python 3.7 compat
        actual_default = default_value.value
    else:
        raise AssertionError(f"Unexpected default value type: {type(default_value)}")

    assert actual_default is False, (
        f"GenerateDashboardRequest.published should default to False (draft state), "
        f"but defaults to {actual_default!r}"
    )


def test_published_field_with_multiple_values():
    """
    Verify the published default across varied analysis - not just one check.

    Type: fail_to_pass
    """
    source = SCHEMA_FILE.read_text()

    # Use regex-based verification as secondary check
    import re

    # Find the published field definition line
    pattern = r'published:\s*bool\s*=\s*Field\s*\(\s*default\s*=\s*(True|False)'
    match = re.search(pattern, source)

    assert match is not None, "Could not find published field with default= in source"

    default_str = match.group(1)
    assert default_str == "False", (
        f"published field should have default=False, found default={default_str}"
    )


def test_schema_file_syntax_valid():
    """
    The schemas.py file should be valid Python syntax.

    Type: pass_to_pass
    """
    source = SCHEMA_FILE.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        raise AssertionError(f"schemas.py has syntax error: {e}")


def test_class_has_required_fields():
    """
    GenerateDashboardRequest should have all required fields.

    Type: pass_to_pass
    """
    source = SCHEMA_FILE.read_text()
    tree = ast.parse(source)

    # Find the class
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GenerateDashboardRequest":
            class_node = node
            break

    assert class_node is not None, "GenerateDashboardRequest class not found"

    # Extract field names
    field_names = set()
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            field_names.add(stmt.target.id)

    # Verify expected fields exist
    expected_fields = {"chart_ids", "dashboard_title", "description", "published"}
    missing = expected_fields - field_names
    assert not missing, f"Missing fields in GenerateDashboardRequest: {missing}"


def test_ruff_lint_schemas():
    """
    Run ruff linter on the schemas file.

    Type: pass_to_pass
    """
    result = subprocess.run(
        ["ruff", "check", str(SCHEMA_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format():
    """
    Run ruff format check on the schemas file (pass_to_pass).

    Verifies that the file follows the project's formatting standards.
    """
    result = subprocess.run(
        ["ruff", "format", "--check", str(SCHEMA_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_mcp_dashboard_module():
    """
    Run ruff linter on the entire mcp_service/dashboard module (pass_to_pass).

    Validates that all Python files in the dashboard module pass linting.
    """
    dashboard_module = REPO / "superset" / "mcp_service" / "dashboard"
    result = subprocess.run(
        ["ruff", "check", str(dashboard_module)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint on dashboard module failed:\n{result.stdout}\n{result.stderr}"


def test_repo_python_syntax_mcp_dashboard():
    """
    Verify all Python files in mcp_service/dashboard have valid syntax (pass_to_pass).

    Uses Python's compile check to validate syntax without needing imports.
    """
    dashboard_module = REPO / "superset" / "mcp_service" / "dashboard"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile"] + [
            str(f) for f in dashboard_module.glob("**/*.py")
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Syntax check failed:\n{result.stderr}"
