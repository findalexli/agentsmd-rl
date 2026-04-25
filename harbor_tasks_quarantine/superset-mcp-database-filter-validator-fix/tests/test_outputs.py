#!/usr/bin/env python3
"""Behavioral tests for MCP database service fixes.

This test suite verifies through code execution:
1. DatabaseFilter includes created_by_fk and changed_by_fk filter columns
2. ListDatabasesRequest field validators parse JSON strings correctly
3. DEFAULT_DATABASE_COLUMNS is imported from schema_discovery (not duplicated)
4. DatabaseError.create() produces timezone-aware timestamps
5. _humanize_timestamp handles both aware and naive datetimes
6. app.py documentation includes database created_by_fk examples
"""

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Path to the superset repository
REPO_PATH = Path("/workspace/superset")


# Docker-internal repo path - the path inside the Docker container
REPO = "/workspace/superset"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO_PATH,
    )


def _run_python_with_output(code: str, timeout: int = 30) -> tuple[int, str, str]:
    """Execute Python code and return (returncode, stdout, stderr)."""
    result = _run_python(code, timeout)
    return result.returncode, result.stdout, result.stderr


# =============================================================================
# Fail-to-Pass (f2p) Tests - Code-Executing Behavioral Tests
# =============================================================================


def test_database_filter_accepts_created_by_fk():
    """DatabaseFilter accepts created_by_fk as valid filter column (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

from superset.mcp_service.database.schemas import DatabaseFilter

# Test that created_by_fk is accepted
filter_obj = DatabaseFilter(col="created_by_fk", opr="eq", value=123)
assert filter_obj.col == "created_by_fk", f"Expected col='created_by_fk', got {filter_obj.col}"
assert filter_obj.opr == "eq"
assert filter_obj.value == 123
print("PASS: DatabaseFilter accepts created_by_fk")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_database_filter_accepts_changed_by_fk():
    """DatabaseFilter accepts changed_by_fk as valid filter column (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

from superset.mcp_service.database.schemas import DatabaseFilter

# Test that changed_by_fk is accepted
filter_obj = DatabaseFilter(col="changed_by_fk", opr="eq", value=456)
assert filter_obj.col == "changed_by_fk", f"Expected col='changed_by_fk', got {filter_obj.col}"
assert filter_obj.opr == "eq"
assert filter_obj.value == 456
print("PASS: DatabaseFilter accepts changed_by_fk")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_list_databases_request_parses_json_filters():
    """ListDatabasesRequest parses JSON string for filters field (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

from superset.mcp_service.database.schemas import ListDatabasesRequest

# Test JSON string parsing for filters
json_filters = '[{"col": "created_by_fk", "opr": "eq", "value": 123}]'
request = ListDatabasesRequest(filters=json_filters)
assert len(request.filters) == 1, f"Expected 1 filter, got {len(request.filters)}"
assert request.filters[0].col == "created_by_fk"
assert request.filters[0].opr == "eq"
assert request.filters[0].value == 123
print("PASS: ListDatabasesRequest parses JSON filters")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_list_databases_request_parses_json_select_columns():
    """ListDatabasesRequest parses JSON string for select_columns field (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

from superset.mcp_service.database.schemas import ListDatabasesRequest

# Test JSON string parsing for select_columns
json_columns = '["id", "database_name", "backend"]'
request = ListDatabasesRequest(select_columns=json_columns)
assert request.select_columns == ["id", "database_name", "backend"], f"Got {request.select_columns}"
print("PASS: ListDatabasesRequest parses JSON select_columns")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_list_databases_imports_default_columns_from_schema_discovery():
    """list_databases.py imports DATABASE_DEFAULT_COLUMNS from schema_discovery (fail_to_pass)."""
    # Check the source code instead of importing (import triggers decorator chain requiring full app)
    file_path = REPO_PATH / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
    assert file_path.exists(), f"File not found: {file_path}"

    content = file_path.read_text()

    # Verify import from schema_discovery (may be lazy import inside function)
    assert "from superset.mcp_service.common.schema_discovery import" in content and \
           "DATABASE_DEFAULT_COLUMNS" in content, \
        "list_databases.py should import DATABASE_DEFAULT_COLUMNS from schema_discovery"

    # Verify the constant is used (not duplicated inline)
    assert "default_columns=DATABASE_DEFAULT_COLUMNS" in content or \
           "DATABASE_DEFAULT_COLUMNS," in content, \
        "list_databases.py should use DATABASE_DEFAULT_COLUMNS constant"


def test_database_error_has_timezone_aware_timestamp():
    """DatabaseError.create() produces timezone-aware timestamps (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

from superset.mcp_service.database.schemas import DatabaseError
from datetime import timezone

# Test that DatabaseError.create() produces timezone-aware timestamp
error = DatabaseError.create(error="Test error", error_type="test")
assert error.timestamp is not None, "Timestamp should not be None"
assert error.timestamp.tzinfo is not None, f"Timestamp should be timezone-aware, got: {error.timestamp.tzinfo}"
print("PASS: DatabaseError.create() produces timezone-aware timestamp")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_humanize_timestamp_handles_aware_datetime():
    """_humanize_timestamp handles timezone-aware datetimes correctly (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

from superset.mcp_service.database.schemas import _humanize_timestamp
from datetime import datetime, timezone, timedelta

# Test with timezone-aware datetime (2 hours ago)
aware_dt = datetime.now(timezone.utc) - timedelta(hours=2)
result = _humanize_timestamp(aware_dt)
assert result is not None, "Should return a string for aware datetime"
assert "hour" in result.lower() or "ago" in result.lower(), f"Expected 'ago' in result, got: {result}"

# Test with naive datetime (should also work)
naive_dt = datetime.now() - timedelta(hours=1)
result_naive = _humanize_timestamp(naive_dt)
assert result_naive is not None, "Should return a string for naive datetime"
print("PASS: _humanize_timestamp handles both aware and naive datetimes")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_app_py_has_database_created_by_fk_documentation():
    """app.py includes database filter examples in documentation (fail_to_pass)."""
    file_path = REPO_PATH / "superset" / "mcp_service" / "app.py"
    assert file_path.exists(), f"File not found: {file_path}"

    with open(file_path) as f:
        content = f.read()

    # Check for databases mentioned alongside charts/dashboards
    assert "charts/dashboards/databases" in content, \
        "app.py should mention databases alongside charts/dashboards"

    # Check for list_databases with created_by_fk example
    assert "list_databases(filters=[" in content and "created_by_fk" in content, \
        "app.py should include list_databases with created_by_fk filter example"

    # Check for "My databases:" section
    assert "My databases:" in content, "app.py should have 'My databases:' example section"


def test_schemas_py_imports_field_validator():
    """schemas.py imports field_validator from pydantic (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

# Verify field_validator can be imported from the schemas module
from superset.mcp_service.database.schemas import field_validator
from pydantic import field_validator as pydantic_validator

# Verify it's the same thing
assert field_validator is pydantic_validator, "field_validator should be from pydantic"
print("PASS: field_validator imported from pydantic")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


def test_schemas_py_imports_parse_utilities():
    """schemas.py imports parse utilities from schema_utils (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/superset")

# Verify parse utilities can be imported from the schemas module
from superset.mcp_service.database.schemas import parse_json_or_list, parse_json_or_model_list

# Verify they are callable
assert callable(parse_json_or_list), "parse_json_or_list should be callable"
assert callable(parse_json_or_model_list), "parse_json_or_model_list should be callable"
print("PASS: parse utilities imported from schema_utils")
"""
    returncode, stdout, stderr = _run_python_with_output(code)
    assert returncode == 0, f"Test failed: {stderr}"
    assert "PASS" in stdout, f"Expected PASS in output: {stdout}"


# =============================================================================
# Pass-to-Pass (p2p) Tests - Repository CI/CD Checks
# =============================================================================


def test_repo_mcp_database_syntax():
    """Modified MCP database files have valid Python syntax (pass_to_pass)."""
    files_to_check = [
        f"{REPO}/superset/mcp_service/database/schemas.py",
        f"{REPO}/superset/mcp_service/database/tool/list_databases.py",
        f"{REPO}/superset/mcp_service/app.py",
        f"{REPO}/superset/mcp_service/mcp_core.py",
    ]
    for file_path in files_to_check:
        result = subprocess.run(
            ["python", "-m", "py_compile", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Syntax error in {file_path}:\n{result.stderr}"


def test_repo_mcp_database_unit_tests():
    """MCP database tools unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        [
            "pip", "install", "-q", "pytest-mock", "pytest-asyncio", "&&",
            "SUPERSET_TESTENV=true",
            "SUPERSET_SECRET_KEY=test",
            "python", "-m", "pytest",
            "tests/unit_tests/mcp_service/database/tool/test_database_tools.py",
            "-v", "--tb=short", "-x",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
        executable="/bin/bash",
        shell=True,
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_repo_mcp_schemas_import():
    """MCP database schemas module imports successfully (pass_to_pass)."""
    code = f"""
import sys
sys.path.insert(0, "{REPO}")

# Test that the schemas module can be imported and has expected classes
from superset.mcp_service.database.schemas import DatabaseFilter, ListDatabasesRequest

# Verify classes are defined (Pydantic models have model_fields)
assert hasattr(DatabaseFilter, 'model_fields'), "DatabaseFilter should be a Pydantic model"
assert hasattr(ListDatabasesRequest, 'model_fields'), "ListDatabasesRequest should be a Pydantic model"

# Verify the classes are instantiable
filter_obj = DatabaseFilter(col="database_name", opr="eq", value="test")
assert filter_obj.col == "database_name", f"Expected col='database_name', got {{filter_obj.col}}"

request_obj = ListDatabasesRequest(page=1, page_size=10)
assert request_obj.page == 1, f"Expected page=1, got {{request_obj.page}}"

print("PASS: MCP database schemas module imports successfully")
"""
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Import test failed:\n{result.stderr}"


def test_repo_mcp_common_schema_discovery():
    """MCP common schema_discovery module imports successfully (pass_to_pass)."""
    code = f"""
import sys
sys.path.insert(0, "{REPO}")

# Test that the schema_discovery module exists and has DATABASE_DEFAULT_COLUMNS
from superset.mcp_service.common.schema_discovery import DATABASE_DEFAULT_COLUMNS

# Verify it's a list/collection
assert isinstance(DATABASE_DEFAULT_COLUMNS, (list, tuple, set)), \
    f"DATABASE_DEFAULT_COLUMNS should be a collection, got {{type(DATABASE_DEFAULT_COLUMNS)}}"
assert len(DATABASE_DEFAULT_COLUMNS) > 0, "DATABASE_DEFAULT_COLUMNS should not be empty"

print("PASS: DATABASE_DEFAULT_COLUMNS imported from schema_discovery")
"""
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"schema_discovery import test failed:\n{result.stderr}"


def test_repo_mcp_service_py_syntax():
    """All MCP service Python files have valid syntax (pass_to_pass)."""
    cmd = f"find {REPO}/superset/mcp_service -name '*.py' -exec python -m py_compile {{}} +"
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        shell=True,
    )
    assert result.returncode == 0, f"Syntax errors found:\n{result.stderr}"


def test_repo_python_unit_tests():
    """Repo Python unit tests for MCP service pass (pass_to_pass)."""
    import os
    # Install required test dependencies
    install_result = subprocess.run(
        ["pip", "install", "-q", "pytest-mock", "pytest-asyncio", "freezegun", "parameterized"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Install errors are logged but not fatal - may already be installed

    # Run MCP service tests - directly relevant to the PR changes
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "./tests/unit_tests/mcp_service/",
            "-v",
            "--tb=short",
            "-x",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env={
            **os.environ,
            "SUPERSET_TESTENV": "true",
            "SUPERSET_SECRET_KEY": "test",
        },
    )
    assert result.returncode == 0, f"MCP unit tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"

# Static Analysis Tests (origin: static - NOT repo_tests)
# =============================================================================


def test_database_schemas_has_database_filter_class():
    """Database schemas module contains DatabaseFilter class (static)."""
    file_path = REPO_PATH / "superset" / "mcp_service" / "database" / "schemas.py"
    assert file_path.exists(), f"File not found: {file_path}"

    tree = ast.parse(file_path.read_text())

    found_class = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DatabaseFilter":
            found_class = True
            break

    assert found_class, "DatabaseFilter class not found in schemas.py"


def test_database_schemas_has_list_databases_request_class():
    """Database schemas module contains ListDatabasesRequest class (static)."""
    file_path = REPO_PATH / "superset" / "mcp_service" / "database" / "schemas.py"

    tree = ast.parse(file_path.read_text())

    found_class = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ListDatabasesRequest":
            found_class = True
            break

    assert found_class, "ListDatabasesRequest class not found in schemas.py"


def test_list_databases_has_tool_function():
    """list_databases.py contains the list_databases tool function (static)."""
    file_path = REPO_PATH / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
    assert file_path.exists(), f"File not found: {file_path}"

    tree = ast.parse(file_path.read_text())

    found_function = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "list_databases":
            found_function = True
            break
        if isinstance(node, ast.FunctionDef) and node.name == "list_databases":
            found_function = True
            break

    assert found_function, "list_databases function not found in list_databases.py"


def test_app_py_has_documentation():
    """app.py contains documentation/instructions (static)."""
    file_path = REPO_PATH / "superset" / "mcp_service" / "app.py"
    assert file_path.exists(), f"File not found: {file_path}"

    content = file_path.read_text()

    # Check for basic structure - should have docstrings and examples
    assert '"""' in content or "'''" in content, "app.py should contain docstrings"
    assert (
        "list_databases" in content
        or "list_charts" in content
        or "list_dashboards" in content
    ), "app.py should reference MCP tools like list_databases, list_charts, or list_dashboards"


# =============================================================================
# Agent Config Tests
# =============================================================================


def test_database_filter_description_updated():
    """DatabaseFilter description mentions created_by_fk usage (agent_config)."""
    file_path = REPO_PATH / "superset" / "mcp_service" / "database" / "schemas.py"

    with open(file_path) as f:
        content = f.read()

    # Check that the description mentions created_by_fk
    assert "created_by_fk with the user" in content, \
        "DatabaseFilter description should mention created_by_fk"
    assert "ID from get_instance_info's current_user" in content, \
        "DatabaseFilter description should reference get_instance_info"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
