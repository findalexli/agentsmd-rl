"""Tests for migration 0097 SQLite foreign key fix."""

import ast
import sys
import os

# Add the repo to path for imports
REPO = "/workspace/airflow"
sys.path.insert(0, os.path.join(REPO, "airflow-core/src"))

MIGRATION_PATH = os.path.join(
    REPO,
    "airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py"
)


def test_migration_file_exists():
    """Verify the migration file exists."""
    assert os.path.exists(MIGRATION_PATH), f"Migration file not found at {MIGRATION_PATH}"


def test_migration_valid_syntax():
    """Verify the migration file is valid Python syntax."""
    with open(MIGRATION_PATH, "r") as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        raise AssertionError(f"Migration file has syntax error: {e}")


def test_update_statements_inside_disable_sqlite_fkeys():
    """
    Verify that UPDATE statements are inside the disable_sqlite_fkeys context.

    This is the core fix: the UPDATE statements must run inside the
    disable_sqlite_fkeys block so that PRAGMA foreign_keys=off executes
    before SQLAlchemy autobegin starts a transaction.
    """
    with open(MIGRATION_PATH, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    # Find the upgrade function
    upgrade_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            upgrade_func = node
            break

    assert upgrade_func is not None, "upgrade() function not found in migration"

    # Check if UPDATE statements are inside disable_sqlite_fkeys context
    # We verify that the with statement containing disable_sqlite_fkeys
    # has the UPDATE execute calls in its body

    found_disable_sqlite_fkeys = False
    has_update_log_in_context = False
    has_update_dag_in_context = False

    for stmt in upgrade_func.body:
        if isinstance(stmt, ast.With):
            # Check if this is the disable_sqlite_fkeys context
            for item in stmt.items:
                context_expr = item.context_expr
                if isinstance(context_expr, ast.Call):
                    func = context_expr.func
                    if isinstance(func, ast.Name) and func.id == "disable_sqlite_fkeys":
                        found_disable_sqlite_fkeys = True

                        # Now check if UPDATE statements are inside this context
                        for inner_stmt in stmt.body:
                            if isinstance(inner_stmt, ast.Expr):
                                value = inner_stmt.value
                                if isinstance(value, ast.Call):
                                    # Check for op.execute calls
                                    if (isinstance(value.func, ast.Attribute) and
                                        value.func.attr == "execute"):
                                        # Check the SQL string
                                        if value.args:
                                            first_arg = value.args[0]
                                            if isinstance(first_arg, ast.Constant):
                                                sql = first_arg.value
                                                if isinstance(sql, str):
                                                    if "UPDATE log SET" in sql:
                                                        has_update_log_in_context = True
                                                    if "UPDATE dag SET" in sql:
                                                        has_update_dag_in_context = True

    assert found_disable_sqlite_fkeys, "disable_sqlite_fkeys context not found in upgrade()"
    assert has_update_log_in_context, "UPDATE log statement must be inside disable_sqlite_fkeys block"
    assert has_update_dag_in_context, "UPDATE dag statement must be inside disable_sqlite_fkeys block"


def test_no_updates_before_disable_sqlite_fkeys():
    """
    Verify that UPDATE statements are NOT before the disable_sqlite_fkeys context.

    This ensures the bug is fixed: before the fix, UPDATE statements ran
    before the with block, causing PRAGMA to be silently ignored.
    """
    with open(MIGRATION_PATH, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    # Find the upgrade function
    upgrade_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            upgrade_func = node
            break

    assert upgrade_func is not None, "upgrade() function not found"

    # Track state: have we seen the with disable_sqlite_fkeys block?
    seen_disable_sqlite_fkeys = False
    updates_before_context = []

    for stmt in upgrade_func.body:
        if isinstance(stmt, ast.With):
            # Check if this is the disable_sqlite_fkeys context
            for item in stmt.items:
                context_expr = item.context_expr
                if isinstance(context_expr, ast.Call):
                    func = context_expr.func
                    if isinstance(func, ast.Name) and func.id == "disable_sqlite_fkeys":
                        seen_disable_sqlite_fkeys = True
                        break

        # Check for UPDATE statements before the context
        if not seen_disable_sqlite_fkeys and isinstance(stmt, ast.Expr):
            value = stmt.value
            if isinstance(value, ast.Call):
                if (isinstance(value.func, ast.Attribute) and
                    value.func.attr == "execute"):
                    if value.args:
                        first_arg = value.args[0]
                        if isinstance(first_arg, ast.Constant):
                            sql = first_arg.value
                            if isinstance(sql, str) and "UPDATE" in sql:
                                updates_before_context.append(sql)

    assert len(updates_before_context) == 0, \
        f"UPDATE statements must NOT be before disable_sqlite_fkeys block: {updates_before_context}"


def test_disable_sqlite_fkeys_context_structure():
    """
    Verify the disable_sqlite_fkeys context has the expected structure.

    The with block should contain both UPDATE statements before the batch_alter_table calls.
    """
    with open(MIGRATION_PATH, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    # Find the upgrade function
    upgrade_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            upgrade_func = node
            break

    assert upgrade_func is not None, "upgrade() function not found"

    # Find the with disable_sqlite_fkeys block
    for stmt in upgrade_func.body:
        if isinstance(stmt, ast.With):
            is_disable_sqlite_block = False
            for item in stmt.items:
                context_expr = item.context_expr
                if isinstance(context_expr, ast.Call):
                    func = context_expr.func
                    if isinstance(func, ast.Name) and func.id == "disable_sqlite_fkeys":
                        is_disable_sqlite_block = True
                        break

            if is_disable_sqlite_block:
                # Count the expected elements in the context
                execute_calls = []
                batch_alter_calls = []

                for inner_stmt in stmt.body:
                    if isinstance(inner_stmt, ast.Expr):
                        value = inner_stmt.value
                        if isinstance(value, ast.Call):
                            if (isinstance(value.func, ast.Attribute) and
                                value.func.attr == "execute"):
                                execute_calls.append(inner_stmt)

                    if isinstance(inner_stmt, ast.With):
                        # Check for batch_alter_table
                        for inner_item in inner_stmt.items:
                            inner_context = inner_item.context_expr
                            if isinstance(inner_context, ast.Call):
                                if (isinstance(inner_context.func, ast.Attribute) and
                                    inner_context.func.attr == "batch_alter_table"):
                                    batch_alter_calls.append(inner_stmt)

                # We should have 2 UPDATE statements and 2 batch_alter_table calls
                assert len(execute_calls) >= 2, \
                    f"Expected at least 2 execute calls (UPDATE statements) in context, found {len(execute_calls)}"
                assert len(batch_alter_calls) == 2, \
                    f"Expected 2 batch_alter_table calls in context, found {len(batch_alter_calls)}"

                # Verify the order: UPDATE statements should come before batch_alter_table
                # We need to check the actual positions
                execute_positions = []
                batch_positions = []

                for i, s in enumerate(stmt.body):
                    if isinstance(s, ast.Expr):
                        value = s.value
                        if isinstance(value, ast.Call):
                            if (isinstance(value.func, ast.Attribute) and
                                value.func.attr == "execute"):
                                execute_positions.append(i)

                    if isinstance(s, ast.With):
                        for item in s.items:
                            context_expr = item.context_expr
                            if isinstance(context_expr, ast.Call):
                                if (isinstance(context_expr.func, ast.Attribute) and
                                    context_expr.func.attr == "batch_alter_table"):
                                    batch_positions.append(i)

                # All UPDATEs should be before batch_alter_table calls
                for ep in execute_positions:
                    for bp in batch_positions:
                        assert ep < bp, \
                            "UPDATE statements must come before batch_alter_table in the context block"

                return  # Success

    raise AssertionError("disable_sqlite_fkeys block with expected structure not found")
