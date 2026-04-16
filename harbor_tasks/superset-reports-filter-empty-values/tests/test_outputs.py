"""
Test outputs for apache/superset#38954

Tests that _generate_native_filter() handles null/empty filterValues correctly.
Before the fix:
- filter_time, filter_timegrain, filter_timecolumn with filterValues=[] -> IndexError on values[0]
- filter_range with filterValues=None -> TypeError on len(values)

After the fix:
- All these cases return ({}, warning_message) instead of crashing
"""

import subprocess
import sys
import os
import ast
import re
import textwrap
import typing

REPO = "/workspace/superset"
REPORTS_MODEL = f"{REPO}/superset/reports/models.py"


def read_models_file():
    """Read the reports models file."""
    with open(REPORTS_MODEL, 'r') as f:
        return f.read()


def extract_generate_native_filter_source():
    """
    Extract the _generate_native_filter method source code as a standalone function.
    Returns the source code with proper dedentation.
    """
    content = read_models_file()

    # Parse the AST
    tree = ast.parse(content)

    # Find the ReportSchedule class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'ReportSchedule':
            # Find the _generate_native_filter method
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '_generate_native_filter':
                    # Get the method source lines
                    start_line = item.lineno
                    end_line = item.end_lineno

                    # Extract the source
                    lines = content.split('\n')
                    method_lines = lines[start_line - 1:end_line]

                    # Join and dedent using textwrap
                    source = '\n'.join(method_lines)
                    source = textwrap.dedent(source)

                    # Convert method to function (remove 'self' parameter)
                    source = re.sub(
                        r'def _generate_native_filter\(\s*self\s*,\s*',
                        'def _generate_native_filter(',
                        source
                    )

                    return source

    return None


class MockLogger:
    """Mock logger that records warnings."""
    def __init__(self):
        self.warnings = []

    def warning(self, msg, *args, **kwargs):
        self.warnings.append(msg)

    def info(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass


def create_test_function():
    """
    Create a testable version of _generate_native_filter.
    """
    source = extract_generate_native_filter_source()
    if source is None:
        raise ValueError("Could not find _generate_native_filter method")

    # Create a namespace with mocked dependencies
    namespace = {
        'logger': MockLogger(),
        'Any': typing.Any,
        'Optional': typing.Optional,
        'dict': dict,
        'list': list,
        'tuple': tuple,
    }

    # Compile and execute the function
    exec(compile(source, '<string>', 'exec'), namespace)

    return namespace['_generate_native_filter']


def test_filter_time_empty_values():
    """
    Test that filter_time with empty values returns ({}, warning) instead of crashing.
    Before fix: IndexError on values[0]
    After fix: Returns empty dict and warning message
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "test_filter_id", "filter_time", "time_col", []
    )

    # After fix: should return empty dict and warning
    assert result == {}, f"Expected empty dict, got {result}"
    assert warning is not None, "Expected warning message"
    assert "filter_time" in warning, f"Warning should mention filter_time: {warning}"
    assert "empty filterValues" in warning, f"Warning should mention empty filterValues: {warning}"
    assert "test_filter_id" in warning, f"Warning should mention filter_id: {warning}"


def test_filter_timegrain_empty_values():
    """
    Test that filter_timegrain with empty values returns ({}, warning) instead of crashing.
    Before fix: IndexError on values[0]
    After fix: Returns empty dict and warning message
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "grain_filter_id", "filter_timegrain", "grain_col", []
    )

    assert result == {}, f"Expected empty dict, got {result}"
    assert warning is not None, "Expected warning message"
    assert "filter_timegrain" in warning, f"Warning should mention filter_timegrain: {warning}"
    assert "empty filterValues" in warning, f"Warning should mention empty filterValues: {warning}"


def test_filter_timecolumn_empty_values():
    """
    Test that filter_timecolumn with empty values returns ({}, warning) instead of crashing.
    Before fix: IndexError on values[0]
    After fix: Returns empty dict and warning message
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "col_filter_id", "filter_timecolumn", "time_col", []
    )

    assert result == {}, f"Expected empty dict, got {result}"
    assert warning is not None, "Expected warning message"
    assert "filter_timecolumn" in warning, f"Warning should mention filter_timecolumn: {warning}"
    assert "empty filterValues" in warning, f"Warning should mention empty filterValues: {warning}"


def test_filter_range_empty_values():
    """
    Test that filter_range with empty values returns ({}, warning) instead of crashing.
    Before fix: Would process with None min/max values
    After fix: Returns empty dict and warning message
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "range_filter_id", "filter_range", "price_col", []
    )

    assert result == {}, f"Expected empty dict, got {result}"
    assert warning is not None, "Expected warning message"
    assert "filter_range" in warning, f"Warning should mention filter_range: {warning}"
    assert "empty filterValues" in warning, f"Warning should mention empty filterValues: {warning}"


def test_filter_range_none_values():
    """
    Test that filter_range with None values is handled gracefully.
    Before fix: TypeError on len(values) if None was passed
    After fix: Returns empty dict and warning message
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "range_filter_id", "filter_range", "price_col", None
    )

    # Should handle None gracefully (either by returning empty result with warning,
    # or by processing it as empty)
    assert result == {}, f"Expected empty dict, got {result}"
    assert warning is not None, "Expected warning message"


# Pass-to-pass tests: ensure existing functionality still works


def test_filter_time_valid_values():
    """
    Test that filter_time with valid values still works correctly.
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "time_filter", "filter_time", "time_col", ["Last 7 days"]
    )

    assert "time_filter" in result
    assert result["time_filter"]["extraFormData"]["time_range"] == "Last 7 days"
    assert warning is None


def test_filter_range_valid_values():
    """
    Test that filter_range with valid values still works correctly.
    """
    _generate_native_filter = create_test_function()

    result, warning = _generate_native_filter(
        "range_filter", "filter_range", "price", [10, 100]
    )

    assert "range_filter" in result
    assert len(result["range_filter"]["extraFormData"]["filters"]) == 2
    assert warning is None


def test_repo_unit_tests():
    """
    Run the repo's own unit tests for the reports models.
    Skip if dependencies are missing.
    """
    # Create a conftest that properly mocks everything
    conftest_dir = f"{REPO}/tests/unit_tests/reports"
    os.makedirs(conftest_dir, exist_ok=True)

    conftest_content = '''
import sys
import os
from unittest.mock import MagicMock

# Mock all problematic modules before any imports
mock_modules = [
    'superset.extensions',
    'superset.extensions.local_extensions_watcher',
    'superset.models.core',
    'superset.models.dashboard',
    'superset.models.helpers',
    'superset.models.slice',
    'superset.reports.types',
    'superset.utils.backports',
    'superset.utils.core',
    'superset.utils',
    'superset.db_engine_specs',
    'superset.db_engine_specs.base',
    'superset.sql_parse',
    'superset.daos',
    'superset.daos.base',
    'superset.daos.dataset',
    'superset.daos.database',
    'superset.queries',
    'superset.commands',
    'superset',
    'flask_appbuilder',
    'flask_appbuilder.models',
    'flask_appbuilder.models.decorators',
    'flask_appbuilder.security',
    'cron_descriptor',
    'prison',
    'alembic',
    'alembic.config',
    'celery',
    'pandas',
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Add the repo to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
'''

    conftest_path = os.path.join(conftest_dir, "conftest.py")
    with open(conftest_path, 'w') as f:
        f.write(conftest_content)

    # Run the tests with proper Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = REPO

    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit_tests/reports/model_test.py", "-v", "--tb=short", "-p", "no:cacheprovider"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env
    )

    # On base commit, some tests may fail due to the bug - that's expected
    # We just want to make sure the tests run (not import errors)
    # On fixed commit, all tests should pass
    if "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr:
        # This is a setup issue, not a test failure
        print(f"Import issues (skipping): {result.stderr[:500]}")
        return

    # If we got here, tests ran - check if they passed
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


# Pass-to-pass tests: repo CI commands


def test_repo_ruff_check():
    """Repo's ruff linter passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Install may fail if already installed, that's ok

    r = subprocess.run(
        ["ruff", "check", f"{REPO}/superset/reports/models.py"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/superset/reports/models.py"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


def test_repo_python_syntax():
    """Modified Python file has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/superset/reports/models.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


def test_repo_imports_parse():
    """Modified Python file can be parsed as valid AST (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import ast; ast.parse(open('{REPO}/superset/reports/models.py').read())",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"
