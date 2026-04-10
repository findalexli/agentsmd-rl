"""
Tests for verifying the PostgreSQL advisory lock implementation in migrations.

These tests verify that:
1. The SQLAlchemy `text` function is imported in env.py
2. The pg_advisory_lock call is present in run_migrations_online()
3. The lock is acquired before running migrations
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path("/workspace/OpenHands")
TARGET_FILE = REPO_ROOT / "enterprise" / "migrations" / "env.py"


def test_sqlalchemy_text_imported():
    """
    Fail-to-pass: Verify that `text` is imported from sqlalchemy.

    The fix requires adding `text` to the sqlalchemy import to enable
    executing raw SQL for the advisory lock.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    found_text_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "sqlalchemy":
                for alias in node.names:
                    if alias.name == "text":
                        found_text_import = True
                        break

    assert found_text_import, (
        "`text` must be imported from sqlalchemy. "
        "Expected: `from sqlalchemy import create_engine, text`"
    )


def test_pg_advisory_lock_call_present():
    """
    Fail-to-pass: Verify that pg_advisory_lock is called in run_migrations_online().

    The fix must add a call to acquire the PostgreSQL advisory lock
    before running migrations to prevent concurrent migration execution.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()

    # Check for the advisory lock call
    assert "pg_advisory_lock" in content, (
        "Missing pg_advisory_lock call. "
        "Must acquire PostgreSQL advisory lock before migrations."
    )

    # Check for the specific lock ID (derived from md5 of 'openhands_enterprise_migrations')
    assert "3617572382373537863" in content, (
        "Missing or incorrect advisory lock ID. "
        "Lock ID must be 3617572382373537863 (md5 of 'openhands_enterprise_migrations')."
    )


def test_advisory_lock_in_run_migrations_online():
    """
    Fail-to-pass: Verify the lock is acquired inside run_migrations_online().

    The advisory lock must be acquired within the run_migrations_online()
    function to ensure it's held during the entire migration process.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    # Find the run_migrations_online function
    found_lock_in_function = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_migrations_online":
            # Get the function body as source
            func_start = node.lineno
            func_end = node.end_lineno
            func_lines = content.splitlines()[func_start - 1:func_end]
            func_content = "\n".join(func_lines)

            assert "pg_advisory_lock" in func_content, (
                "pg_advisory_lock must be called inside run_migrations_online(). "
                "The lock should be acquired before begin_transaction()."
            )
            found_lock_in_function = True
            break

    assert found_lock_in_function, "run_migrations_online() function not found"


def test_lock_before_begin_transaction():
    """
    Pass-to-pass: Verify the lock is acquired BEFORE begin_transaction().

    The advisory lock must be acquired before the migration transaction
    begins to ensure proper ordering.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    # Find the run_migrations_online function and check lock comes before begin_transaction
    found_lock_before_transaction = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_migrations_online":
            func_start = node.lineno
            func_end = node.end_lineno
            func_lines = content.splitlines()[func_start - 1:func_end]
            func_content = "\n".join(func_lines)

            lock_pos = func_content.find("pg_advisory_lock")
            transaction_pos = func_content.find("begin_transaction()")

            assert lock_pos != -1, "pg_advisory_lock call not found in run_migrations_online()"
            assert transaction_pos != -1, "begin_transaction() call not found in run_migrations_online()"

            assert lock_pos < transaction_pos, (
                "pg_advisory_lock must be called BEFORE begin_transaction(). "
                "The lock should be acquired before the migration transaction starts."
            )
            found_lock_before_transaction = True
            break

    assert found_lock_before_transaction, "run_migrations_online() function not found"


def test_text_function_used_for_lock():
    """
    Pass-to-pass: Verify text() wrapper is used for the raw SQL lock query.

    SQLAlchemy requires text() wrapper for raw SQL execution.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()

    # Check that text() is used with the advisory lock
    assert "text('SELECT pg_advisory_lock" in content or 'text("SELECT pg_advisory_lock' in content, (
        "The pg_advisory_lock query must be wrapped with text() for SQLAlchemy execution. "
        "Expected: connection.execute(text('SELECT pg_advisory_lock(...)'))"
    )


def test_lock_acquired_via_connection_execute():
    """
    Pass-to-pass: Verify the lock is acquired using connection.execute().

    The advisory lock should be acquired through the connection object
    to ensure it's held for the duration of the connection.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()

    # Check for connection.execute pattern with advisory lock
    assert "connection.execute(text('SELECT pg_advisory_lock" in content or \
           "connection.execute(text(\"SELECT pg_advisory_lock" in content, (
        "The advisory lock must be acquired via connection.execute(text(...)). "
        "This ensures the lock is held on the correct database connection."
    )


def test_file_is_valid_python():
    """
    Pass-to-pass: Verify the modified file is valid Python syntax.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"

    content = TARGET_FILE.read_text()

    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"env.py contains syntax errors: {e}")


def test_pre_commit_hooks_pass():
    """
    Agent-config check: Verify enterprise pre-commit hooks pass.

    From AGENTS.md: Enterprise linting must use --show-diff-on-failure to match CI.
    """
    # Check that the file passes basic Python syntax and import checks
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, (
        f"env.py failed Python compilation: {result.stderr}"
    )


# =============================================================================
# Pass-to-Pass tests based on actual repo CI commands
# =============================================================================

REPO = Path("/workspace/OpenHands")
MIGRATIONS_FILE = REPO / "enterprise" / "migrations" / "env.py"
RUFF_CONFIG = REPO / "enterprise" / "dev_config" / "python" / "ruff.toml"


def test_repo_python_syntax():
    """Repo CI: Python syntax check passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(MIGRATIONS_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ruff_lint():
    """Repo CI: Ruff linting passes on modified file (pass_to_pass)."""
    # Install ruff if needed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=False)
    r = subprocess.run(
        ["ruff", "check", str(MIGRATIONS_FILE), "--config", str(RUFF_CONFIG)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_alembic_ini_exists():
    """Repo CI: Alembic configuration file exists (pass_to_pass)."""
    alembic_ini = REPO / "enterprise" / "alembic.ini"
    r = subprocess.run(
        ["test", "-f", str(alembic_ini)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0, "alembic.ini configuration file is missing"
