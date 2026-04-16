"""Test outputs for Superset MCP MAX_PAGE_SIZE enforcement task.

This module uses file inspection and AST parsing to verify the MAX_PAGE_SIZE
limit is properly enforced across:
1. Chart list schema validation
2. Dashboard list schema validation
3. Dataset list schema validation
4. ModelListCore defense-in-depth clamping

We use AST/file inspection rather than imports to avoid needing full
Superset dependencies (Flask, SQLAlchemy, etc.).
"""

import ast
import inspect
import re
import subprocess
import sys
from pathlib import Path

# Repository path
REPO = Path("/workspace/superset")


def parse_file(file_path: Path) -> ast.Module:
    """Parse a Python file and return the AST."""
    content = file_path.read_text()
    return ast.parse(content)


def find_imports(tree: ast.Module) -> list:
    """Find all imports in an AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    return imports


def test_constants_defined():
    """Test that MAX_PAGE_SIZE and DEFAULT_PAGE_SIZE constants are defined."""
    constants_file = REPO / "superset" / "mcp_service" / "constants.py"
    assert constants_file.exists(), f"constants.py should exist at {constants_file}"

    tree = parse_file(constants_file)

    # Find all assignments
    found_max = False
    found_default = False
    max_value = None
    default_value = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "MAX_PAGE_SIZE":
                        found_max = True
                        if isinstance(node.value, ast.Constant):
                            max_value = node.value.value
                    elif target.id == "DEFAULT_PAGE_SIZE":
                        found_default = True
                        if isinstance(node.value, ast.Constant):
                            default_value = node.value.value

    assert found_max, "MAX_PAGE_SIZE constant should be defined"
    assert found_default, "DEFAULT_PAGE_SIZE constant should be defined"
    assert max_value == 100, f"MAX_PAGE_SIZE should be 100, got {max_value}"
    assert default_value == 10, f"DEFAULT_PAGE_SIZE should be 10, got {default_value}"


def test_constants_file_has_expected_values():
    """Test that constants.py contains the expected pagination constants as text."""
    constants_file = REPO / "superset" / "mcp_service" / "constants.py"
    assert constants_file.exists(), f"constants.py should exist at {constants_file}"

    content = constants_file.read_text()

    # Check for the constants
    assert "DEFAULT_PAGE_SIZE = 10" in content, "constants.py should define DEFAULT_PAGE_SIZE = 10"
    assert "MAX_PAGE_SIZE = 100" in content, "constants.py should define MAX_PAGE_SIZE = 100"

    # Check they are in the right order/section
    assert "Pagination defaults" in content or "# Pagination" in content, \
        "constants.py should have a comment indicating pagination defaults section"


def test_schemas_import_constants():
    """Test that schema files import the pagination constants."""
    schemas_to_check = [
        REPO / "superset" / "mcp_service" / "chart" / "schemas.py",
        REPO / "superset" / "mcp_service" / "dashboard" / "schemas.py",
        REPO / "superset" / "mcp_service" / "dataset" / "schemas.py",
    ]

    for schema_file in schemas_to_check:
        assert schema_file.exists(), f"Schema file should exist: {schema_file}"
        content = schema_file.read_text()

        # Check import of constants
        assert "from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE" in content, \
            f"{schema_file.name} should import DEFAULT_PAGE_SIZE and MAX_PAGE_SIZE"

        # Check that page_size field uses MAX_PAGE_SIZE
        assert "le=MAX_PAGE_SIZE" in content, \
            f"{schema_file.name} should use le=MAX_PAGE_SIZE constraint on page_size field"


def test_chart_schema_page_size_validation():
    """Test that ListChartsRequest has proper page_size validation."""
    schema_file = REPO / "superset" / "mcp_service" / "chart" / "schemas.py"
    assert schema_file.exists(), f"Schema file should exist: {schema_file}"

    content = schema_file.read_text()

    # Check import
    assert "from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE" in content, \
        "chart/schemas.py should import pagination constants"

    # Find the ListChartsRequest class and page_size field
    tree = parse_file(schema_file)

    found_list_charts = False
    found_page_size_constraint = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ListChartsRequest":
            found_list_charts = True
            # Check if page_size field uses le=MAX_PAGE_SIZE
            # We check by looking for the pattern in the source
            class_source = ast.get_source_segment(content, node) or ""
            if "le=MAX_PAGE_SIZE" in class_source or "le= MAX_PAGE_SIZE" in class_source:
                found_page_size_constraint = True

    # Also check via text search for robustness
    if not found_page_size_constraint:
        # Check the file content for le=MAX_PAGE_SIZE near page_size
        assert "le=MAX_PAGE_SIZE" in content, \
            "chart/schemas.py should use le=MAX_PAGE_SIZE constraint"


def test_dashboard_schema_page_size_validation():
    """Test that ListDashboardsRequest has proper page_size validation."""
    schema_file = REPO / "superset" / "mcp_service" / "dashboard" / "schemas.py"
    assert schema_file.exists(), f"Schema file should exist: {schema_file}"

    content = schema_file.read_text()

    # Check import
    assert "from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE" in content, \
        "dashboard/schemas.py should import pagination constants"

    # Check the constraint exists
    assert "le=MAX_PAGE_SIZE" in content, \
        "dashboard/schemas.py should use le=MAX_PAGE_SIZE constraint"


def test_dataset_schema_page_size_validation():
    """Test that ListDatasetsRequest has proper page_size validation."""
    schema_file = REPO / "superset" / "mcp_service" / "dataset" / "schemas.py"
    assert schema_file.exists(), f"Schema file should exist: {schema_file}"

    content = schema_file.read_text()

    # Check import
    assert "from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE" in content, \
        "dataset/schemas.py should import pagination constants"

    # Check the constraint exists
    assert "le=MAX_PAGE_SIZE" in content, \
        "dataset/schemas.py should use le=MAX_PAGE_SIZE constraint"


def test_mcp_core_clamps_page_size():
    """Test that ModelListCore.run_tool clamps page_size to MAX_PAGE_SIZE."""
    mcp_core_file = REPO / "superset" / "mcp_service" / "mcp_core.py"
    assert mcp_core_file.exists(), f"mcp_core.py should exist at {mcp_core_file}"

    content = mcp_core_file.read_text()

    # Check that MAX_PAGE_SIZE is imported in run_tool method
    assert "MAX_PAGE_SIZE" in content, "MAX_PAGE_SIZE should be referenced in mcp_core.py"

    # Verify that min() clamping is present
    assert "min(page_size, MAX_PAGE_SIZE)" in content, \
        "run_tool should clamp page_size using min(page_size, MAX_PAGE_SIZE)"

    # Verify the defense-in-depth comment
    assert "Clamp page_size" in content or "defense-in-depth" in content.lower(), \
        "Should have a comment explaining the clamping as defense-in-depth"


def test_main_py_has_middleware():
    """Test that __main__.py adds default middleware stack."""
    main_file = REPO / "superset" / "mcp_service" / "__main__.py"
    assert main_file.exists(), f"__main__.py should exist at {main_file}"

    content = main_file.read_text()

    # Check for middleware addition function
    assert "_add_default_middlewares" in content, \
        "__main__.py should define _add_default_middlewares function"

    # Check that middlewares are added in both stdio and other transport modes
    # Count occurrences - should be called at least twice (once for stdio, once for other)
    call_count = content.count("_add_default_middlewares()")
    assert call_count >= 2, \
        f"__main__.py should call _add_default_middlewares() at least twice (found {call_count})"

    # Check that key middlewares are imported/added
    assert "create_response_size_guard_middleware" in content, \
        "__main__.py should import and use response size guard middleware"

    assert "GlobalErrorHandlerMiddleware" in content, \
        "__main__.py should use GlobalErrorHandlerMiddleware"

    assert "LoggingMiddleware" in content, \
        "__main__.py should use LoggingMiddleware"


def test_chart_schema_uses_default_page_size():
    """Test that chart schema uses DEFAULT_PAGE_SIZE as the default value."""
    schema_file = REPO / "superset" / "mcp_service" / "chart" / "schemas.py"
    content = schema_file.read_text()

    # Check that DEFAULT_PAGE_SIZE is used as the default
    assert "default=DEFAULT_PAGE_SIZE" in content, \
        "chart/schemas.py should use default=DEFAULT_PAGE_SIZE"


def test_dashboard_schema_uses_default_page_size():
    """Test that dashboard schema uses DEFAULT_PAGE_SIZE as the default value."""
    schema_file = REPO / "superset" / "mcp_service" / "dashboard" / "schemas.py"
    content = schema_file.read_text()

    assert "default=DEFAULT_PAGE_SIZE" in content, \
        "dashboard/schemas.py should use default=DEFAULT_PAGE_SIZE"


def test_dataset_schema_uses_default_page_size():
    """Test that dataset schema uses DEFAULT_PAGE_SIZE as the default value."""
    schema_file = REPO / "superset" / "mcp_service" / "dataset" / "schemas.py"
    content = schema_file.read_text()

    assert "default=DEFAULT_PAGE_SIZE" in content, \
        "dataset/schemas.py should use default=DEFAULT_PAGE_SIZE"


# =============================================================================
# Pass-to-Pass Tests (Repo CI Commands)
# =============================================================================

def test_constants_py_syntax():
    """Repo: constants.py has valid Python syntax (pass_to_pass).

    Verifies that the constants file compiles without syntax errors.
    This is a lightweight CI check that doesn't require full dependencies.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", "superset/mcp_service/constants.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error in constants.py: {result.stderr}"


def test_chart_schemas_py_syntax():
    """Repo: chart/schemas.py has valid Python syntax (pass_to_pass).

    Verifies that the chart schema file compiles without syntax errors.
    This is a lightweight CI check that doesn't require full dependencies.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", "superset/mcp_service/chart/schemas.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error in chart/schemas.py: {result.stderr}"


def test_dashboard_schemas_py_syntax():
    """Repo: dashboard/schemas.py has valid Python syntax (pass_to_pass).

    Verifies that the dashboard schema file compiles without syntax errors.
    This is a lightweight CI check that doesn't require full dependencies.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", "superset/mcp_service/dashboard/schemas.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error in dashboard/schemas.py: {result.stderr}"


def test_dataset_schemas_py_syntax():
    """Repo: dataset/schemas.py has valid Python syntax (pass_to_pass).

    Verifies that the dataset schema file compiles without syntax errors.
    This is a lightweight CI check that doesn't require full dependencies.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", "superset/mcp_service/dataset/schemas.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error in dataset/schemas.py: {result.stderr}"


def test_mcp_core_py_syntax():
    """Repo: mcp_core.py has valid Python syntax (pass_to_pass).

    Verifies that the mcp_core file compiles without syntax errors.
    This is a lightweight CI check that doesn't require full dependencies.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", "superset/mcp_service/mcp_core.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error in mcp_core.py: {result.stderr}"


def test_main_py_syntax():
    """Repo: __main__.py has valid Python syntax (pass_to_pass).

    Verifies that the main file compiles without syntax errors.
    This is a lightweight CI check that doesn't require full dependencies.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", "superset/mcp_service/__main__.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error in __main__.py: {result.stderr}"


def test_chart_schema_ast_valid():
    """Repo: chart/schemas.py has valid AST structure with ListChartsRequest (pass_to_pass).

    Uses AST parsing to verify the schema structure without importing.
    Checks that ListChartsRequest class exists and has expected structure.
    """
    result = subprocess.run(
        [
            "python3", "-c",
            """
import ast
with open('superset/mcp_service/chart/schemas.py') as f:
    tree = ast.parse(f.read())

# Find ListChartsRequest class
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ListChartsRequest':
        found = True
        break

assert found, 'ListChartsRequest class not found'
print('ListChartsRequest class found')
"""
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"AST validation failed: {result.stderr}"


def test_dashboard_schema_ast_valid():
    """Repo: dashboard/schemas.py has valid AST structure with ListDashboardsRequest (pass_to_pass).

    Uses AST parsing to verify the schema structure without importing.
    Checks that ListDashboardsRequest class exists and has expected structure.
    """
    result = subprocess.run(
        [
            "python3", "-c",
            """
import ast
with open('superset/mcp_service/dashboard/schemas.py') as f:
    tree = ast.parse(f.read())

# Find ListDashboardsRequest class
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ListDashboardsRequest':
        found = True
        break

assert found, 'ListDashboardsRequest class not found'
print('ListDashboardsRequest class found')
"""
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"AST validation failed: {result.stderr}"


def test_dataset_schema_ast_valid():
    """Repo: dataset/schemas.py has valid AST structure with ListDatasetsRequest (pass_to_pass).

    Uses AST parsing to verify the schema structure without importing.
    Checks that ListDatasetsRequest class exists and has expected structure.
    """
    result = subprocess.run(
        [
            "python3", "-c",
            """
import ast
with open('superset/mcp_service/dataset/schemas.py') as f:
    tree = ast.parse(f.read())

# Find ListDatasetsRequest class
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ListDatasetsRequest':
        found = True
        break

assert found, 'ListDatasetsRequest class not found'
print('ListDatasetsRequest class found')
"""
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"AST validation failed: {result.stderr}"
