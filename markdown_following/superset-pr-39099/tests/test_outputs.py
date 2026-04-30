"""
Tests for apache/superset#39099: Check pre-existing foreign keys on create utility

These tests verify:
1. The new get_foreign_key_names() helper function exists and works
2. create_fks_for_table() gracefully handles pre-existing foreign keys
3. drop_fks_for_table() still works after refactoring to use the helper
"""

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/superset")
UTILS_PATH = REPO / "superset" / "migrations" / "shared" / "utils.py"


def load_utils_module():
    """Load the utils module directly without going through superset package."""
    spec = importlib.util.spec_from_file_location("utils", UTILS_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules['superset'] = MagicMock()
    sys.modules['superset.utils'] = MagicMock()
    sys.modules['superset.utils.core'] = MagicMock()
    spec.loader.exec_module(module)
    return module


# =============================================================================
# FAIL-TO-PASS TESTS - These must fail on base commit, pass after fix
# =============================================================================


def test_get_foreign_key_names_exists():
    """Verify that the get_foreign_key_names() helper function exists.

    (fail_to_pass) This function was added by the PR.
    """
    utils = load_utils_module()

    assert hasattr(utils, 'get_foreign_key_names'), \
        "get_foreign_key_names function not found in utils module"
    assert callable(utils.get_foreign_key_names), \
        "get_foreign_key_names should be callable"


def test_get_foreign_key_names_returns_set():
    """Verify that get_foreign_key_names() returns a set of FK names.

    (fail_to_pass) The function must return a set[str].
    """
    utils = load_utils_module()

    mock_connection = MagicMock()
    mock_inspector = MagicMock()
    mock_inspector.get_foreign_keys.return_value = [
        {"name": "fk_test_1", "constrained_columns": ["col1"]},
        {"name": "fk_test_2", "constrained_columns": ["col2"]},
    ]

    with patch.object(utils, 'op') as mock_op, \
         patch.object(utils, 'Inspector') as mock_inspector_cls, \
         patch.object(utils, 'inspect', return_value=mock_inspector):
        mock_op.get_bind.return_value = mock_connection
        mock_op.get_context.return_value.bind = mock_connection
        mock_inspector_cls.from_engine.return_value = mock_inspector

        result = utils.get_foreign_key_names("test_table")

        assert isinstance(result, set), f"Expected set, got {type(result)}"
        assert result == {"fk_test_1", "fk_test_2"}, f"Unexpected result: {result}"


def test_get_foreign_key_names_empty_table():
    """Verify get_foreign_key_names() returns empty set for table with no FKs.

    (fail_to_pass) Function must handle tables without foreign keys.
    """
    utils = load_utils_module()

    mock_connection = MagicMock()
    mock_inspector = MagicMock()
    mock_inspector.get_foreign_keys.return_value = []

    with patch.object(utils, 'op') as mock_op, \
         patch.object(utils, 'Inspector') as mock_inspector_cls, \
         patch.object(utils, 'inspect', return_value=mock_inspector):
        mock_op.get_bind.return_value = mock_connection
        mock_op.get_context.return_value.bind = mock_connection
        mock_inspector_cls.from_engine.return_value = mock_inspector

        result = utils.get_foreign_key_names("empty_table")

        assert result == set(), f"Expected empty set, got {result}"


def test_get_foreign_key_names_multiple_tables():
    """Verify get_foreign_key_names() works with different table names.

    (fail_to_pass) Function must handle various table names.
    """
    utils = load_utils_module()

    mock_connection = MagicMock()
    mock_inspector = MagicMock()

    def mock_get_fks(table_name):
        if table_name == "table_a":
            return [{"name": "fk_a1"}, {"name": "fk_a2"}]
        elif table_name == "table_b":
            return [{"name": "fk_b1"}]
        return []

    mock_inspector.get_foreign_keys = mock_get_fks

    with patch.object(utils, 'op') as mock_op, \
         patch.object(utils, 'Inspector') as mock_inspector_cls, \
         patch.object(utils, 'inspect', return_value=mock_inspector):
        mock_op.get_bind.return_value = mock_connection
        mock_op.get_context.return_value.bind = mock_connection
        mock_inspector_cls.from_engine.return_value = mock_inspector

        result_a = utils.get_foreign_key_names("table_a")
        result_b = utils.get_foreign_key_names("table_b")
        result_c = utils.get_foreign_key_names("table_c")

        assert result_a == {"fk_a1", "fk_a2"}
        assert result_b == {"fk_b1"}
        assert result_c == set()


def test_create_fks_skips_existing_foreign_key():
    """Verify create_fks_for_table() skips creating FK if it already exists.

    (fail_to_pass) Before the fix, this would attempt to create a duplicate FK
    which would raise a database error.
    """
    utils = load_utils_module()

    mock_connection = MagicMock()
    mock_connection.dialect = MagicMock()
    type(mock_connection.dialect).__name__ = "PostgresDialect"

    mock_inspector = MagicMock()
    mock_inspector.get_foreign_keys.return_value = [
        {"name": "existing_fk", "constrained_columns": ["user_id"]}
    ]

    with patch.object(utils, 'op') as mock_op, \
         patch.object(utils, 'Inspector') as mock_inspector_cls, \
         patch.object(utils, 'inspect', return_value=mock_inspector), \
         patch.object(utils, 'has_table', return_value=True), \
         patch.object(utils, 'logger') as mock_logger, \
         patch.object(utils, 'SQLiteDialect', MagicMock()):

        mock_op.get_bind.return_value = mock_connection
        mock_op.get_context.return_value.bind = mock_connection
        mock_inspector_cls.from_engine.return_value = mock_inspector

        utils.create_fks_for_table(
            foreign_key_name="existing_fk",
            table_name="test_table",
            referenced_table="users",
            local_cols=["user_id"],
            remote_cols=["id"]
        )

        mock_op.create_foreign_key.assert_not_called()

        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("already exists" in call or "Skipping" in call for call in log_calls), \
            f"Expected log message about skipping existing FK, got: {log_calls}"


def test_create_fks_skips_various_existing_fks():
    """Verify create_fks_for_table() skips for different FK names.

    (fail_to_pass) The check should work for any FK name, not just hardcoded ones.
    """
    utils = load_utils_module()

    for fk_name in ["fk_user_dashboard", "fk_slice_datasource", "custom_constraint_name"]:
        mock_connection = MagicMock()
        mock_connection.dialect = MagicMock()
        type(mock_connection.dialect).__name__ = "PostgresDialect"

        mock_inspector = MagicMock()
        mock_inspector.get_foreign_keys.return_value = [{"name": fk_name}]

        with patch.object(utils, 'op') as mock_op, \
             patch.object(utils, 'Inspector') as mock_inspector_cls, \
             patch.object(utils, 'inspect', return_value=mock_inspector), \
             patch.object(utils, 'has_table', return_value=True), \
             patch.object(utils, 'logger'), \
             patch.object(utils, 'SQLiteDialect', MagicMock()):

            mock_op.get_bind.return_value = mock_connection
            mock_op.get_context.return_value.bind = mock_connection
            mock_inspector_cls.from_engine.return_value = mock_inspector

            utils.create_fks_for_table(
                foreign_key_name=fk_name,
                table_name="test_table",
                referenced_table="users",
                local_cols=["col"],
                remote_cols=["id"]
            )

            mock_op.create_foreign_key.assert_not_called(), \
                f"Should skip existing FK: {fk_name}"


def test_drop_fks_uses_helper_function():
    """Verify drop_fks_for_table() uses get_foreign_key_names helper internally.

    (fail_to_pass) After refactoring, drop_fks_for_table should call the helper.
    """
    utils = load_utils_module()

    assert hasattr(utils, 'get_foreign_key_names'), \
        "get_foreign_key_names function not found - drop_fks_for_table should use the shared helper"

    mock_connection = MagicMock()
    mock_connection.dialect = MagicMock()

    with patch.object(utils, 'op') as mock_op, \
         patch.object(utils, 'get_foreign_key_names', return_value={"fk_1"}) as mock_helper, \
         patch.object(utils, 'has_table', return_value=True), \
         patch.object(utils, 'logger'):

        mock_op.get_bind.return_value = mock_connection

        utils.drop_fks_for_table("test_table")

        mock_helper.assert_called_with("test_table")


# =============================================================================
# PASS-TO-PASS TESTS - These must pass on both base commit and after fix
# =============================================================================


def test_syntax_valid():
    """Verify the utils.py file is syntactically valid Python.

    (pass_to_pass) Basic syntax check.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", str(UTILS_PATH)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Syntax error in utils.py:\n{result.stderr}"


def test_module_loads():
    """Verify the utils module can be loaded without errors.

    (pass_to_pass) Module should load cleanly.
    """
    try:
        utils = load_utils_module()
        assert utils is not None
    except Exception as e:
        pytest.fail(f"Failed to load utils module: {e}")


def test_has_table_function_exists():
    """Verify has_table helper function exists (used by create_fks_for_table).

    (pass_to_pass) This function should exist in both versions.
    """
    utils = load_utils_module()
    assert hasattr(utils, 'has_table'), "has_table function should exist"
    assert callable(utils.has_table), "has_table should be callable"


def test_create_fks_for_table_exists():
    """Verify create_fks_for_table function exists.

    (pass_to_pass) Function should exist in both versions.
    """
    utils = load_utils_module()
    assert hasattr(utils, 'create_fks_for_table'), "create_fks_for_table should exist"
    assert callable(utils.create_fks_for_table), "create_fks_for_table should be callable"


def test_drop_fks_for_table_exists():
    """Verify drop_fks_for_table function exists.

    (pass_to_pass) Function should exist in both versions.
    """
    utils = load_utils_module()
    assert hasattr(utils, 'drop_fks_for_table'), "drop_fks_for_table should exist"
    assert callable(utils.drop_fks_for_table), "drop_fks_for_table should be callable"


def test_type_hints_present():
    """Verify the modified functions have type hints.

    (pass_to_pass) Type hints should be present per repo standards.
    """
    source = UTILS_PATH.read_text()

    assert "def create_fks_for_table(" in source
    assert "def drop_fks_for_table(" in source

    assert "-> None:" in source, "Functions should have return type hints"


def test_logging_imported():
    """Verify logging functionality is available.

    (pass_to_pass) Logger should be set up in both versions.
    """
    source = UTILS_PATH.read_text()
    assert "logger" in source, "Logger should be used in utils.py"
    assert "logging" in source or "getLogger" in source, \
        "Logging should be imported or configured"


def test_repo_ruff_lint():
    """Run ruff linter on the modified file via bash -lc (CI-style invocation).

    (pass_to_pass) Ruff linting must pass per repo CI.
    """
    result = subprocess.run(
        ["bash", "-lc", f"ruff check {UTILS_PATH} --select=E,F,W --ignore=E501"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format():
    """Run ruff format check on the modified file.

    (pass_to_pass) Code must be properly formatted per repo CI.
    """
    result = subprocess.run(
        ["ruff", "format", "--check", str(UTILS_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_imports_valid():
    """Verify the utils.py has valid import statements.

    (pass_to_pass) All imports at top of file must be parseable.
    """
    source = UTILS_PATH.read_text()
    try:
        tree = ast.parse(source)
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        assert len(imports) > 0, "File should have imports"
    except SyntaxError as e:
        pytest.fail(f"AST parse failed: {e}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_check_for_uncommitted_changes():
    """pass_to_pass | CI job 'check-python-deps' → step 'Check for uncommitted changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Full diff (for logging/debugging):"\ngit diff\n\necho "Filtered diff (excluding comments and whitespace):"\nfiltered_diff=$(git diff -U0 | grep \'^[-+]\' | grep -vE \'^[-+]{3}\' | grep -vE \'^[-+][[:space:]]*#\' | grep -vE \'^[-+][[:space:]]*$\' || true)\necho "$filtered_diff"\n\nif [[ -n "$filtered_diff" ]]; then\n  echo\n  echo "ERROR: The pinned dependencies are not up-to-date."\n  echo "Please run \'./scripts/uv-pip-compile.sh\' and commit the changes."\n  echo "More info: https://github.com/apache/superset/tree/master/requirements"\n  exit 1\nelse\n  echo "Pinned dependencies are up-to-date."\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for uncommitted changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_load_examples_superset_init():
    """pass_to_pass | CI job 'test-load-examples' → step 'superset init'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'superset init' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_frontend_check_translations_lint():
    """pass_to_pass | CI job 'frontend-check-translations' → step 'lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build-translation'], cwd=os.path.join(REPO, './superset-frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run ci:release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_python_unit_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Python unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --durations-min=0.5 --cov-report= --cov=superset ./tests/common ./tests/unit_tests --cache-clear --maxfail=50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_python_100_coverage_unit_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Python 100% coverage unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --durations-min=0.5 --cov=superset/sql/ ./tests/unit_tests/sql/ --cache-clear --cov-fail-under=100'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python 100% coverage unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_python_integration_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres' → step 'Python integration tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")