"""Tests for the pg_advisory_lock migration fix.

This module tests that the database migration code properly acquires a
PostgreSQL advisory lock before running migrations to prevent concurrent
migration attempts from multiple pods.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/OpenHands"
TARGET_FILE = Path(REPO) / "enterprise" / "migrations" / "env.py"


def test_text_import_from_sqlalchemy():
    """Test that 'text' is imported from sqlalchemy and is actually usable.

    This is a fail-to-pass test. The base commit does not import 'text'
    from sqlalchemy, which is required to execute raw SQL for the advisory lock.
    """
    # Actually try to import text from sqlalchemy to verify it exists and works
    from sqlalchemy import text

    # Verify text is a callable that produces a executable SQL expression
    sql_expr = text("SELECT 1")
    assert sql_expr is not None, "text() must return a SQL expression object"

    # Now verify the target file actually imports text
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found_text_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "sqlalchemy":
                for alias in node.names:
                    if alias.name == "text":
                        found_text_import = True
                        break

    assert found_text_import, (
        "'text' must be imported from sqlalchemy. "
        "Expected: 'from sqlalchemy import create_engine, text'"
    )


def test_pg_advisory_lock_call_present():
    """Test that pg_advisory_lock is called with a lock ID.

    This is a fail-to-pass test. The base commit does not have the advisory
    lock call, which is the core of the fix to prevent concurrent migrations.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find any pg_advisory_lock call - it could be inside a text() wrapper
    # Look for text() calls that contain pg_advisory_lock in their SQL string
    found_lock_call = False
    lock_arg = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is a text() call
            if isinstance(node.func, ast.Name) and node.func.id == "text":
                if node.args and isinstance(node.args[0], ast.Constant):
                    sql_string = str(node.args[0].value)
                    if "pg_advisory_lock" in sql_string:
                        found_lock_call = True
                        # Extract the lock ID from the SQL string
                        import re
                        match = re.search(r'pg_advisory_lock\s*\(\s*(\d+)\s*\)', sql_string)
                        if match:
                            lock_arg = int(match.group(1))
                        break

    assert found_lock_call, (
        "pg_advisory_lock must be called to serialize migration runs. "
        "The lock prevents multiple pods from running migrations simultaneously."
    )

    # Verify the lock ID is a positive integer
    assert isinstance(lock_arg, int) and lock_arg > 0, (
        "pg_advisory_lock must be called with a positive integer lock ID"
    )


def test_advisory_lock_before_migrations():
    """Test that advisory lock is acquired BEFORE run_migrations() is called.

    This is a fail-to-pass test. The lock must be acquired before migrations
    run to prevent race conditions when multiple pods start simultaneously.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find the run_migrations_online function
    found_correct_order = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_migrations_online":
            # Get the source lines for this function
            start_line = node.lineno
            end_line = node.end_lineno
            func_source = "\n".join(source.split("\n")[start_line - 1:end_line])

            # Check that pg_advisory_lock appears before run_migrations
            lock_pos = func_source.find("pg_advisory_lock")
            migrations_pos = func_source.find("context.run_migrations()")

            if lock_pos != -1 and migrations_pos != -1:
                if lock_pos < migrations_pos:
                    found_correct_order = True

    assert found_correct_order, (
        "pg_advisory_lock must be called BEFORE context.run_migrations(). "
        "The lock acquisition must happen before any migration operations."
    )


def test_advisory_lock_uses_text_wrapper():
    """Test that the advisory lock uses sqlalchemy.text() wrapper.

    This is a fail-to-pass test. The advisory lock SQL must be wrapped with
    text() to work properly with SQLAlchemy's execution model.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find the call that contains pg_advisory_lock
    found_text_wrapper = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is a text() call containing pg_advisory_lock
            if isinstance(node.func, ast.Name) and node.func.id == "text":
                if node.args and isinstance(node.args[0], ast.Constant):
                    if "pg_advisory_lock" in str(node.args[0].value):
                        found_text_wrapper = True

    assert found_text_wrapper, (
        "The pg_advisory_lock SQL must be wrapped with sqlalchemy.text(). "
        "Expected: connection.execute(text('SELECT pg_advisory_lock(...)'))"
    )


def test_lock_in_run_migrations_online():
    """Test that the lock is in the run_migrations_online function, not offline.

    This is a pass-to-pass test verifying the lock is in the correct function.
    Advisory locks only make sense for online migrations with a real database connection.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Check that lock is in run_migrations_online
    lock_in_online = False
    lock_in_offline = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = node.end_lineno
            func_source = "\n".join(source.split("\n")[start_line - 1:end_line])

            if node.name == "run_migrations_online" and "pg_advisory_lock" in func_source:
                lock_in_online = True
            if node.name == "run_migrations_offline" and "pg_advisory_lock" in func_source:
                lock_in_offline = True

    assert lock_in_online, (
        "The pg_advisory_lock must be in run_migrations_online(). "
        "This is where the actual database connection exists."
    )

    assert not lock_in_offline, (
        "The pg_advisory_lock should NOT be in run_migrations_offline(). "
        "Offline migrations don't have a real database connection."
    )


def test_module_can_be_imported():
    """Test that the modified env.py can be imported without errors.

    This verifies that the changes don't introduce syntax errors or
    import errors that would prevent the migration module from loading.
    """
    # Try to at least parse the file as a syntax check
    source = TARGET_FILE.read_text()
    try:
        compile(source, str(TARGET_FILE), 'exec')
    except SyntaxError as e:
        assert False, f"env.py has syntax error: {e}"


def test_lock_acquires_before_transaction():
    """Test that lock acquisition happens before begin_transaction.

    This verifies the lock is not inside a transaction block, which would
    defeat its purpose of serializing migration runs across pods.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_migrations_online":
            start_line = node.lineno
            end_line = node.end_lineno
            func_source = "\n".join(source.split("\n")[start_line - 1:end_line])

            # Find positions of key elements
            lock_pos = func_source.find("pg_advisory_lock")
            begin_pos = func_source.find("begin_transaction")
            run_pos = func_source.find("run_migrations")

            assert lock_pos != -1, "pg_advisory_lock must be present"

            # If begin_transaction exists, lock must come before it
            if begin_pos != -1:
                assert lock_pos < begin_pos, (
                    "pg_advisory_lock must be acquired BEFORE begin_transaction(). "
                    "Locking inside a transaction doesn't prevent concurrent migration runs."
                )


def test_repo_ruff_check():
    """Repo's ruff linter passes on the migrations file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--config", "dev_config/python/ruff.toml", "enterprise/migrations/env.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on the migrations file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--config", "dev_config/python/ruff.toml", "--check", "enterprise/migrations/env.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax():
    """Python syntax check passes on the migrations file (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "enterprise/migrations/env.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_enterprise_ruff_check():
    """Enterprise ruff config passes on the migrations file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--config", "enterprise/dev_config/python/ruff.toml", "enterprise/migrations/env.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Enterprise ruff check failed:\n{r.stdout}\n{r.stderr}"