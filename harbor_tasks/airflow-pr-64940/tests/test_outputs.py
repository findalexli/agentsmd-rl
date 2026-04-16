#!/usr/bin/env python3
"""
Behavioral tests for apache/airflow#64940: fix(migrations): move UPDATEs inside disable_sqlite_fkeys

These tests actually EXECUTE the migration code and verify behavior, not just text.
The tests verify that:
1. UPDATE statements execute AFTER PRAGMA foreign_keys=off inside the context
2. The migration is syntactically valid
3. All required SQL statements are present
"""

import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/airflow")
MIGRATION_FILE = REPO / "airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py"


class TestMigration0097ExecutionOrder:
    """Tests that verify UPDATE statements execute AFTER PRAGMA foreign_keys=off."""

    def test_update_log_executes_after_pragma_via_subprocess(self):
        """UPDATE log must execute after PRAGMA foreign_keys=off (fail_to_pass).
        
        This test verifies actual execution order by running a script that:
        1. Imports the migration using importlib (avoiding airflow package init)
        2. Mocks op.execute to track SQL execution order
        3. Calls upgrade() and asserts PRAGMA comes before UPDATE
        """
        check_script = r"""
import sys
import importlib.util

utils_spec = importlib.util.spec_from_file_location(
    'airflow.migrations.utils',
    '/workspace/airflow/airflow-core/src/airflow/migrations/utils.py'
)
utils_module = importlib.util.module_from_spec(utils_spec)
utils_spec.loader.exec_module(utils_module)

sys.modules['airflow.migrations.utils'] = utils_module

spec = importlib.util.spec_from_file_location("migration", sys.argv[1])
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

# execution_log entries: (inside_context, sql_statement)
execution_log = []

class MockOp:
    def execute(self, sql):
        execution_log.append((inside_context[0], str(sql)))
        return None
    
    def get_bind(self):
        return MagicMock(dialect=MagicMock(name="sqlite"))
    
    def batch_alter_table(self, *args, **kwargs):
        class MockBatch:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def alter_column(self, *args, **kwargs): pass
        return MockBatch()

inside_context = [False]

def mock_disable_sqlite_fkeys(op):
    from contextlib import contextmanager
    
    @contextmanager
    def cm():
        inside_context[0] = True
        # Track PRAGMA as inside context
        execution_log.append((inside_context[0], "PRAGMA foreign_keys=off"))
        yield op
        execution_log.append((inside_context[0], "PRAGMA foreign_keys=on"))
        inside_context[0] = False
    
    return cm()

# Set up the mock op and inject into migration namespace
mock_op_instance = MockOp()
migration.op = mock_op_instance
migration.disable_sqlite_fkeys = mock_disable_sqlite_fkeys

# Also patch utils_module
original_disable = utils_module.disable_sqlite_fkeys
utils_module.disable_sqlite_fkeys = mock_disable_sqlite_fkeys

try:
    migration.upgrade()
except Exception as e:
    print(f"Error during upgrade: {e}", file=sys.stderr)

utils_module.disable_sqlite_fkeys = original_disable

# Find PRAGMA and UPDATE log positions
pragma_idx = None
update_log_idx = None

for i, (ctx, sql) in enumerate(execution_log):
    if pragma_idx is None and "PRAGMA foreign_keys=off" in sql:
        pragma_idx = i
    if update_log_idx is None and "UPDATE log" in sql:
        update_log_idx = i

errors = []
if pragma_idx is None:
    errors.append("PRAGMA foreign_keys=off never executed")
if update_log_idx is None:
    errors.append("UPDATE log never executed")

if errors:
    print("ERROR: " + "; ".join(errors))
    sys.exit(1)

# Check: PRAGMA must come BEFORE UPDATE log
if pragma_idx >= update_log_idx:
    print(f"ERROR: PRAGMA (index {pragma_idx}) must execute before UPDATE log (index {update_log_idx})")
    sys.exit(1)

# Check: UPDATE log should be inside context (ctx=True means inside)
ctx_for_update = None
for i, (ctx, sql) in enumerate(execution_log):
    if "UPDATE log" in sql:
        ctx_for_update = ctx
        break

if not ctx_for_update:
    print("ERROR: UPDATE log must execute inside disable_sqlite_fkeys context")
    sys.exit(1)

print("OK: UPDATE log executes after PRAGMA foreign_keys=off inside context")
sys.exit(0)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(check_script)
            script_path = f.name
        
        try:
            result = subprocess.run(
                ["python3", script_path, str(MIGRATION_FILE)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO,
                env={**os.environ, "PYTHONPATH": str(REPO / "airflow-core/src")}
            )
            assert result.returncode == 0, (
                f"Execution order test failed. stdout: {result.stdout}, stderr: {result.stderr}"
            )
            assert "OK" in result.stdout, f"Test failed: {result.stdout}"
        finally:
            os.unlink(script_path)

    def test_update_dag_executes_after_pragma_via_subprocess(self):
        """UPDATE dag must execute after PRAGMA foreign_keys=off (fail_to_pass).
        
        Same as above but for UPDATE dag statement.
        """
        check_script = r"""
import sys
import importlib.util

utils_spec = importlib.util.spec_from_file_location(
    'airflow.migrations.utils',
    '/workspace/airflow/airflow-core/src/airflow/migrations/utils.py'
)
utils_module = importlib.util.module_from_spec(utils_spec)
utils_spec.loader.exec_module(utils_module)

sys.modules['airflow.migrations.utils'] = utils_module

spec = importlib.util.spec_from_file_location("migration", sys.argv[1])
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

execution_log = []

class MockOp:
    def execute(self, sql):
        execution_log.append((inside_context[0], str(sql)))
        return None
    
    def get_bind(self):
        return MagicMock(dialect=MagicMock(name="sqlite"))
    
    def batch_alter_table(self, *args, **kwargs):
        class MockBatch:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def alter_column(self, *args, **kwargs): pass
        return MockBatch()

inside_context = [False]

def mock_disable_sqlite_fkeys(op):
    from contextlib import contextmanager
    
    @contextmanager
    def cm():
        inside_context[0] = True
        execution_log.append((inside_context[0], "PRAGMA foreign_keys=off"))
        yield op
        execution_log.append((inside_context[0], "PRAGMA foreign_keys=on"))
        inside_context[0] = False
    
    return cm()

mock_op_instance = MockOp()
migration.op = mock_op_instance
migration.disable_sqlite_fkeys = mock_disable_sqlite_fkeys

original_disable = utils_module.disable_sqlite_fkeys
utils_module.disable_sqlite_fkeys = mock_disable_sqlite_fkeys

try:
    migration.upgrade()
except Exception as e:
    print(f"Error during upgrade: {e}", file=sys.stderr)

utils_module.disable_sqlite_fkeys = original_disable

pragma_idx = None
update_dag_idx = None

for i, (ctx, sql) in enumerate(execution_log):
    if pragma_idx is None and "PRAGMA foreign_keys=off" in sql:
        pragma_idx = i
    if update_dag_idx is None and "UPDATE dag" in sql:
        update_dag_idx = i

errors = []
if pragma_idx is None:
    errors.append("PRAGMA foreign_keys=off never executed")
if update_dag_idx is None:
    errors.append("UPDATE dag never executed")

if errors:
    print("ERROR: " + "; ".join(errors))
    sys.exit(1)

if pragma_idx >= update_dag_idx:
    print(f"ERROR: PRAGMA (index {pragma_idx}) must execute before UPDATE dag (index {update_dag_idx})")
    sys.exit(1)

ctx_for_update = None
for i, (ctx, sql) in enumerate(execution_log):
    if "UPDATE dag" in sql:
        ctx_for_update = ctx
        break

if not ctx_for_update:
    print("ERROR: UPDATE dag must execute inside disable_sqlite_fkeys context")
    sys.exit(1)

print("OK: UPDATE dag executes after PRAGMA foreign_keys=off inside context")
sys.exit(0)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(check_script)
            script_path = f.name
        
        try:
            result = subprocess.run(
                ["python3", script_path, str(MIGRATION_FILE)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO,
                env={**os.environ, "PYTHONPATH": str(REPO / "airflow-core/src")}
            )
            assert result.returncode == 0, (
                f"Execution order test failed. stdout: {result.stdout}, stderr: {result.stderr}"
            )
            assert "OK" in result.stdout, f"Test failed: {result.stdout}"
        finally:
            os.unlink(script_path)


class TestMigrationSQLiteFKBehavior:
    """Tests that verify SQLite FK pragma behavior."""

    def test_pragma_executes_before_any_update(self):
        """PRAGMA foreign_keys=off must execute before any UPDATE statement (fail_to_pass).
        
        This verifies the core bug fix: the pragma must run first, before any
        transaction-starting UPDATE.
        """
        check_script = r"""
import sys
import importlib.util

utils_spec = importlib.util.spec_from_file_location(
    'airflow.migrations.utils',
    '/workspace/airflow/airflow-core/src/airflow/migrations/utils.py'
)
utils_module = importlib.util.module_from_spec(utils_spec)
utils_spec.loader.exec_module(utils_module)

sys.modules['airflow.migrations.utils'] = utils_module

spec = importlib.util.spec_from_file_location("migration", sys.argv[1])
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

execution_log = []

class MockOp:
    def execute(self, sql):
        execution_log.append((inside_context[0], str(sql)))
        return None
    
    def get_bind(self):
        return MagicMock(dialect=MagicMock(name="sqlite"))
    
    def batch_alter_table(self, *args, **kwargs):
        class MockBatch:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def alter_column(self, *args, **kwargs): pass
        return MockBatch()

inside_context = [False]

def mock_disable_sqlite_fkeys(op):
    from contextlib import contextmanager
    
    @contextmanager
    def cm():
        inside_context[0] = True
        execution_log.append((inside_context[0], "PRAGMA foreign_keys=off"))
        yield op
        execution_log.append((inside_context[0], "PRAGMA foreign_keys=on"))
        inside_context[0] = False
    
    return cm()

mock_op_instance = MockOp()
migration.op = mock_op_instance
migration.disable_sqlite_fkeys = mock_disable_sqlite_fkeys

original = utils_module.disable_sqlite_fkeys
utils_module.disable_sqlite_fkeys = mock_disable_sqlite_fkeys

try:
    migration.upgrade()
except:
    pass

utils_module.disable_sqlite_fkeys = original

# Find indices - pragma must come before first UPDATE
pragma_idx = None
first_update_idx = None

for i, (ctx, sql) in enumerate(execution_log):
    if pragma_idx is None and "PRAGMA foreign_keys=off" in sql:
        pragma_idx = i
    if first_update_idx is None and ("UPDATE log" in sql or "UPDATE dag" in sql):
        first_update_idx = i

if pragma_idx is None:
    print("ERROR: PRAGMA foreign_keys=off never executed")
    sys.exit(1)

if first_update_idx is None:
    print("ERROR: No UPDATE statements found")
    sys.exit(1)

if pragma_idx >= first_update_idx:
    print(f"ERROR: PRAGMA must execute before first UPDATE. PRAGMA at {pragma_idx}, first UPDATE at {first_update_idx}")
    sys.exit(1)

print(f"OK: PRAGMA executes at index {pragma_idx}, first UPDATE at index {first_update_idx}")
sys.exit(0)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(check_script)
            script_path = f.name
        
        try:
            result = subprocess.run(
                ["python3", script_path, str(MIGRATION_FILE)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO,
                env={**os.environ, "PYTHONPATH": str(REPO / "airflow-core/src")}
            )
            assert result.returncode == 0, (
                f"FK pragma timing test failed. stdout: {result.stdout}, stderr: {result.stderr}"
            )
            assert "OK" in result.stdout, f"Test failed: {result.stdout}"
        finally:
            os.unlink(script_path)


class TestMigrationSyntax:
    """Pass-to-pass tests ensuring migration remains valid."""

    def test_migration_file_exists(self):
        """Migration file must exist (pass_to_pass)."""
        assert MIGRATION_FILE.exists(), f"Migration file not found: {MIGRATION_FILE}"

    def test_migration_file_syntax_valid(self):
        """Migration file must have valid Python syntax (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Migration file has syntax error: {e}")

    def test_migration_imports_disable_sqlite_fkeys(self):
        """Migration must import disable_sqlite_fkeys utility (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()
        assert "disable_sqlite_fkeys" in source, "disable_sqlite_fkeys import missing"

    def test_migration_has_upgrade_function(self):
        """Migration must have upgrade() function (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()
        tree = ast.parse(source)

        has_upgrade = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
                has_upgrade = True
                break

        assert has_upgrade, "upgrade() function not found in migration"

    def test_migration_has_batch_alter_table(self):
        """Migration must use batch_alter_table for SQLite compatibility (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()
        assert "batch_alter_table" in source, (
            "batch_alter_table not found - required for SQLite ALTER COLUMN"
        )

    def test_migration_alters_event_column(self):
        """Migration must alter the event column to NOT NULL (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()
        assert 'alter_column("event"' in source or "alter_column('event'" in source, (
            "Migration must alter the 'event' column"
        )

    def test_migration_sets_nullable_false(self):
        """Migration must set nullable=False for event column (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()
        assert "nullable=False" in source, (
            "Migration must set nullable=False for the event column"
        )


class TestUpdateStatementContent:
    """Tests verifying the UPDATE statements have correct content."""

    def test_update_log_sets_empty_string_for_null(self):
        """UPDATE log must set event='' for NULL values (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()

        # Must contain this exact update logic
        assert "UPDATE log SET event = '' WHERE event IS NULL" in source or \
               "UPDATE log SET event = \"\" WHERE event IS NULL" in source, (
            "UPDATE log statement must set event to empty string for NULL values"
        )

    def test_update_dag_sets_false_for_null(self):
        """UPDATE dag must set is_stale=false for NULL values (pass_to_pass)."""
        source = MIGRATION_FILE.read_text()

        # Must contain this exact update logic
        assert "UPDATE dag SET is_stale = false WHERE is_stale IS NULL" in source, (
            "UPDATE dag statement must set is_stale to false for NULL values"
        )


class TestRepoCICommands:
    """Pass-to-pass tests that run actual repo CI commands via subprocess."""

    def test_repo_migration_compiles(self):
        """Migration file passes Python compilation check (pass_to_pass).
        
        This runs `python -m py_compile` which is a standard CI check.
        """
        result = subprocess.run(
            ["python", "-m", "py_compile", str(MIGRATION_FILE)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Migration file failed py_compile:\n{result.stderr}"
        )

    def test_repo_migration_valid_structure(self):
        """Migration has valid alembic structure (pass_to_pass).
        
        This runs a Python command to validate the migration has required elements:
        - revision and down_revision attributes
        - upgrade() and downgrade() functions
        """
        check_script = """
import sys
import ast
from pathlib import Path

migration_path = sys.argv[1]
source = Path(migration_path).read_text()
tree = ast.parse(source)

has_revision = False
has_down_revision = False
has_upgrade = False
has_downgrade = False

for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id == "revision":
                    has_revision = True
                elif target.id == "down_revision":
                    has_down_revision = True
    elif isinstance(node, ast.FunctionDef):
        if node.name == "upgrade":
            has_upgrade = True
        elif node.name == "downgrade":
            has_downgrade = True

errors = []
if not has_revision:
    errors.append("Missing revision attribute")
if not has_down_revision:
    errors.append("Missing down_revision attribute")
if not has_upgrade:
    errors.append("Missing upgrade() function")
if not has_downgrade:
    errors.append("Missing downgrade() function")

if errors:
    print("Migration structure errors: " + ", ".join(errors))
    sys.exit(1)
print("Migration structure OK")
"""
        result = subprocess.run(
            ["python", "-c", check_script, str(MIGRATION_FILE)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Migration structure check failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_repo_migration_no_assert_statements(self):
        """Migration has no assert statements in production code (pass_to_pass).
        
        Assertions are stripped in optimized Python, so migrations must not
        use assert for validation.
        """
        check_script = """
import sys
import ast
from pathlib import Path

migration_path = sys.argv[1]
source = Path(migration_path).read_text()
tree = ast.parse(source)

asserts_found = []
for node in ast.walk(tree):
    if isinstance(node, ast.Assert):
        asserts_found.append(f"line {node.lineno}")

if asserts_found:
    print(f"Found assert statements at: {', '.join(asserts_found)}")
    sys.exit(1)
print("No assert statements found")
"""
        result = subprocess.run(
            ["python", "-c", check_script, str(MIGRATION_FILE)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Migration contains assert statements:\n{result.stdout}\n{result.stderr}"
        )
