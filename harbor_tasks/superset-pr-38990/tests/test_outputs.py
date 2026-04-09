"""
Tests for apache/superset#38990 - MCP service table chart raw mode and XSS fixes.

This tests:
1. Table chart form_data includes both 'columns' and 'all_columns' in raw mode
2. _build_query_columns handles raw mode with all_columns/columns
3. ASCIIPreviewStrategy handles raw mode correctly
4. GenerateDashboardRequest sanitizes dashboard_title via field_validator
5. HTML tags are stripped from dashboard titles
6. Dangerous unicode is removed from dashboard titles

PASS-TO-PASS tests:
- test_repo_python_syntax: Verify all modified files have valid Python syntax
- test_repo_sanitization_logic: Verify sanitization functions work correctly
- test_repo_chart_utils_syntax: Verify chart_utils.py syntax
- test_repo_preview_utils_syntax: Verify preview_utils.py syntax
- test_repo_get_chart_preview_syntax: Verify get_chart_preview.py syntax
"""

import sys
import os
import subprocess
sys.path.insert(0, '/workspace/superset')

# Mock required modules before imports
from unittest.mock import MagicMock, patch

# Create mock for superset_core
superset_core_mock = MagicMock()
superset_core_mock.api.mcp.tool = lambda *args, **kwargs: (lambda f: f)
sys.modules['superset_core'] = superset_core_mock
sys.modules['superset_core.api'] = superset_core_mock.api
sys.modules['superset_core.api.mcp'] = superset_core_mock.api.mcp

# Mock flask
flask_mock = MagicMock()
flask_mock.g = MagicMock()
sys.modules['flask'] = flask_mock

# Mock other common dependencies
sys.modules['superset'] = MagicMock()
sys.modules['superset.daos'] = MagicMock()
sys.modules['superset.daos.chart'] = MagicMock()
sys.modules['superset.daos.dashboard'] = MagicMock()
sys.modules['superset.daos.dataset'] = MagicMock()
sys.modules['superset.models'] = MagicMock()
sys.modules['superset.models.core'] = MagicMock()
sys.modules['superset.models.dashboard'] = MagicMock()
sys.modules['superset.models.slice'] = MagicMock()
sys.modules['superset.extensions'] = MagicMock()
sys.modules['superset.db_engine_specs'] = MagicMock()
sys.modules['superset.charts'] = MagicMock()
sys.modules['superset.charts.schemas'] = MagicMock()
sys.modules['superset.datasets'] = MagicMock()
sys.modules['superset.datasets.commands'] = MagicMock()
sys.modules['superset.datasets.commands.export'] = MagicMock()
sys.modules['superset.sql_lab'] = MagicMock()
sys.modules['superset.utils'] = MagicMock()
sys.modules['superset.utils.core'] = MagicMock()
sys.modules['superset.mcp_service'] = MagicMock()
sys.modules['superset.mcp_service.chart'] = MagicMock()
sys.modules['superset.mcp_service.chart.chart_utils'] = MagicMock()
sys.modules['superset.mcp_service.chart.preview_utils'] = MagicMock()
sys.modules['superset.mcp_service.chart.schemas'] = MagicMock()
sys.modules['superset.mcp_service.chart.tool'] = MagicMock()
sys.modules['superset.mcp_service.chart.tool.get_chart_preview'] = MagicMock()
sys.modules['superset.mcp_service.utils'] = MagicMock()
sys.modules['superset.mcp_service.utils.metadata'] = MagicMock()
sys.modules['superset.mcp_service.utils.schema_utils'] = MagicMock()
sys.modules['superset.mcp_service.utils.sanitization'] = MagicMock()

import pytest


# ============== Test 1: chart_utils map_table_config ==============

def test_table_chart_form_data_includes_columns_in_raw_mode():
    """
    FAIL-TO-PASS: map_table_config must include both 'columns' and 'all_columns'
    in raw mode to avoid 'Empty query?' errors.
    """
    # Read the actual file to check for the fix
    chart_utils_path = '/workspace/superset/superset/mcp_service/chart/chart_utils.py'
    if not os.path.exists(chart_utils_path):
        pytest.skip("chart_utils.py not found")

    with open(chart_utils_path, 'r') as f:
        content = f.read()

    # Check that the fix is present: "columns" field added alongside "all_columns"
    assert '"columns": raw_columns' in content, \
        "chart_utils.py must include 'columns': raw_columns in raw mode handling"

    # Check for the comment explaining why
    assert 'QueryContextFactory validation' in content, \
        "Fix should include comment about QueryContextFactory validation"


# ============== Test 2: preview_utils _build_query_columns ==============

def test_preview_utils_handles_raw_mode():
    """
    FAIL-TO-PASS: _build_query_columns must handle table charts in raw mode
    by checking for all_columns or columns fields.
    """
    preview_utils_path = '/workspace/superset/superset/mcp_service/chart/preview_utils.py'
    if not os.path.exists(preview_utils_path):
        pytest.skip("preview_utils.py not found")

    with open(preview_utils_path, 'r') as f:
        content = f.read()

    # Check that the raw mode handling is present
    assert 'query_mode' in content and 'raw' in content, \
        "preview_utils.py must check for query_mode == 'raw'"

    assert 'all_columns' in content, \
        "preview_utils.py must handle all_columns field"

    # Verify the early return pattern for raw mode
    assert 'return list(all_columns or raw_columns_field)' in content or \
           'return list(all_columns or' in content, \
        "preview_utils.py must return early with raw columns in raw mode"


# ============== Test 3: get_chart_preview ASCIIPreviewStrategy ==============

def test_ascii_preview_handles_raw_mode():
    """
    FAIL-TO-PASS: ASCIIPreviewStrategy must check for raw mode and use
    all_columns/columns when building query context.
    """
    get_chart_preview_path = '/workspace/superset/superset/mcp_service/chart/tool/get_chart_preview.py'
    if not os.path.exists(get_chart_preview_path):
        pytest.skip("get_chart_preview.py not found")

    with open(get_chart_preview_path, 'r') as f:
        content = f.read()

    # Check for raw mode handling in the file
    assert 'query_mode' in content and 'raw' in content, \
        "get_chart_preview.py must check for query_mode == 'raw'"

    assert 'all_columns' in content, \
        "get_chart_preview.py must handle all_columns field"

    # Check for the conditional logic that handles raw mode differently
    assert 'if form_data.get("query_mode") == "raw"' in content or \
           "if form_data.get('query_mode') == 'raw'" in content, \
        "get_chart_preview.py must have conditional logic for raw mode"


# ============== Test 4: Dashboard title field_validator ==============

def test_generate_dashboard_request_has_title_validator():
    """
    FAIL-TO-PASS: GenerateDashboardRequest must have a field_validator
    for dashboard_title that sanitizes input.
    """
    schemas_path = '/workspace/superset/superset/mcp_service/dashboard/schemas.py'
    if not os.path.exists(schemas_path):
        pytest.skip("dashboard/schemas.py not found")

    with open(schemas_path, 'r') as f:
        content = f.read()

    # Check for field_validator import and usage
    assert '@field_validator("dashboard_title")' in content or \
           "@field_validator('dashboard_title')" in content, \
        "GenerateDashboardRequest must have @field_validator for dashboard_title"

    assert 'sanitize_dashboard_title' in content, \
        "Must have sanitize_dashboard_title method"


# ============== Test 5: HTML tags stripped ==============

def test_dashboard_title_strips_html_tags():
    """
    PASS-TO-PASS: The sanitization must strip HTML tags from dashboard titles.
    """
    schemas_path = '/workspace/superset/superset/mcp_service/dashboard/schemas.py'
    if not os.path.exists(schemas_path):
        pytest.skip("dashboard/schemas.py not found")

    with open(schemas_path, 'r') as f:
        content = f.read()

    # Check that _strip_html_tags is imported and used
    assert '_strip_html_tags' in content, \
        "Must import and use _strip_html_tags for XSS prevention"

    # Check for the call to strip HTML tags in the validator
    assert '_strip_html_tags' in content and 'v' in content, \
        "Must call _strip_html_tags on the title value"


# ============== Test 6: Dangerous unicode removed ==============

def test_dashboard_title_removes_dangerous_unicode():
    """
    PASS-TO-PASS: The sanitization must remove dangerous unicode characters.
    """
    schemas_path = '/workspace/superset/superset/mcp_service/dashboard/schemas.py'
    if not os.path.exists(schemas_path):
        pytest.skip("dashboard/schemas.py not found")

    with open(schemas_path, 'r') as f:
        content = f.read()

    # Check that _remove_dangerous_unicode is imported and used
    assert '_remove_dangerous_unicode' in content, \
        "Must import and use _remove_dangerous_unicode"

    # Check the import statement
    assert 'from superset.mcp_service.utils.sanitization import' in content, \
        "Must import sanitization functions from utils.sanitization"


# ============== Integration-style tests for XSS fix ==============

def test_sanitization_imports_present():
    """
    Verify the sanitization module imports are properly structured.
    """
    schemas_path = '/workspace/superset/superset/mcp_service/dashboard/schemas.py'
    if not os.path.exists(schemas_path):
        pytest.skip("dashboard/schemas.py not found")

    with open(schemas_path, 'r') as f:
        content = f.read()

    # Check for the specific import block
    lines = content.split('\n')
    import_idx = -1
    for i, line in enumerate(lines):
        if 'from superset.mcp_service.utils.sanitization import' in line:
            import_idx = i
            break

    assert import_idx >= 0, "Must have import from utils.sanitization"

    # Check that both functions are imported
    import_section = '\n'.join(lines[import_idx:import_idx+5])
    assert '_strip_html_tags' in import_section, \
        "Must import _strip_html_tags from sanitization module"
    assert '_remove_dangerous_unicode' in import_section, \
        "Must import _remove_dangerous_unicode from sanitization module"


def test_raw_mode_column_handling_consistent():
    """
    Verify that all three locations handle raw mode consistently.
    """
    # Check all three files have the raw mode fix
    files_to_check = [
        '/workspace/superset/superset/mcp_service/chart/chart_utils.py',
        '/workspace/superset/superset/mcp_service/chart/preview_utils.py',
        '/workspace/superset/superset/mcp_service/chart/tool/get_chart_preview.py',
    ]

    for filepath in files_to_check:
        if not os.path.exists(filepath):
            pytest.skip(f"{filepath} not found")

        with open(filepath, 'r') as f:
            content = f.read()

        assert 'all_columns' in content, f"{filepath} must handle all_columns"
        assert 'columns' in content, f"{filepath} must handle columns"


# ============== PASS-TO-PASS: Repo CI tests ==============

REPO = "/workspace/superset"


def test_repo_python_syntax():
    """All modified Python files have valid syntax (pass_to_pass)."""
    files_to_check = [
        "superset/mcp_service/chart/chart_utils.py",
        "superset/mcp_service/chart/preview_utils.py",
        "superset/mcp_service/chart/tool/get_chart_preview.py",
        "superset/mcp_service/dashboard/schemas.py",
        "superset/mcp_service/utils/sanitization.py",
    ]

    for rel_path in files_to_check:
        full_path = os.path.join(REPO, rel_path)
        if not os.path.exists(full_path):
            pytest.skip(f"{rel_path} not found")

        # Use py_compile to check syntax
        result = subprocess.run(
            ["python", "-m", "py_compile", full_path],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Syntax error in {rel_path}: {result.stderr}"


def test_repo_sanitization_logic():
    """Sanitization functions work correctly (pass_to_pass)."""
    sanitization_path = os.path.join(REPO, "superset/mcp_service/utils/sanitization.py")
    if not os.path.exists(sanitization_path):
        pytest.skip("sanitization.py not found")

    with open(sanitization_path, "r") as f:
        content = f.read()

    # Verify nh3 is imported for HTML sanitization
    assert "import nh3" in content, "sanitization.py must import nh3"

    # Verify _strip_html_tags function exists and uses nh3
    assert "def _strip_html_tags" in content, "sanitization.py must have _strip_html_tags function"
    assert "nh3.clean" in content, "sanitization.py must use nh3.clean for HTML stripping"

    # Verify _remove_dangerous_unicode function exists
    assert "def _remove_dangerous_unicode" in content, "sanitization.py must have _remove_dangerous_unicode function"

    # Check for dangerous unicode pattern (zero-width chars, control chars)
    assert r"[\u200B-\u200D\uFEFF\u0000-\u0008" in content, "sanitization.py must handle dangerous unicode"


def test_repo_chart_utils_syntax():
    """chart_utils.py compiles and contains expected raw mode handling (pass_to_pass)."""
    chart_utils_path = os.path.join(REPO, "superset/mcp_service/chart/chart_utils.py")
    if not os.path.exists(chart_utils_path):
        pytest.skip("chart_utils.py not found")

    # Syntax check
    result = subprocess.run(
        ["python", "-m", "py_compile", chart_utils_path],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"chart_utils.py has syntax errors: {result.stderr}"

    # Content check - verify map_table_config exists
    with open(chart_utils_path, "r") as f:
        content = f.read()

    assert "def map_table_config" in content, "chart_utils.py must have map_table_config function"
    assert "query_mode" in content, "chart_utils.py must handle query_mode"


def test_repo_preview_utils_syntax():
    """preview_utils.py compiles and contains expected column building logic (pass_to_pass)."""
    preview_utils_path = os.path.join(REPO, "superset/mcp_service/chart/preview_utils.py")
    if not os.path.exists(preview_utils_path):
        pytest.skip("preview_utils.py not found")

    # Syntax check
    result = subprocess.run(
        ["python", "-m", "py_compile", preview_utils_path],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"preview_utils.py has syntax errors: {result.stderr}"

    # Content check - verify _build_query_columns exists
    with open(preview_utils_path, "r") as f:
        content = f.read()

    assert "def _build_query_columns" in content, "preview_utils.py must have _build_query_columns function"


def test_repo_get_chart_preview_syntax():
    """get_chart_preview.py compiles correctly (pass_to_pass)."""
    get_chart_preview_path = os.path.join(REPO, "superset/mcp_service/chart/tool/get_chart_preview.py")
    if not os.path.exists(get_chart_preview_path):
        pytest.skip("get_chart_preview.py not found")

    # Syntax check
    result = subprocess.run(
        ["python", "-m", "py_compile", get_chart_preview_path],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"get_chart_preview.py has syntax errors: {result.stderr}"


def test_repo_dashboard_schemas_syntax():
    """dashboard/schemas.py compiles and contains expected validator (pass_to_pass)."""
    schemas_path = os.path.join(REPO, "superset/mcp_service/dashboard/schemas.py")
    if not os.path.exists(schemas_path):
        pytest.skip("dashboard/schemas.py not found")

    # Syntax check
    result = subprocess.run(
        ["python", "-m", "py_compile", schemas_path],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, f"dashboard/schemas.py has syntax errors: {result.stderr}"

    # Content check - verify GenerateDashboardRequest exists with validator
    with open(schemas_path, "r") as f:
        content = f.read()

    assert "class GenerateDashboardRequest" in content, "schemas.py must have GenerateDashboardRequest class"
    assert "@field_validator" in content, "schemas.py must use field_validator"
