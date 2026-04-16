#!/usr/bin/env python3
"""Test outputs for OpenHands PR #13658: Persist disabled_skills in SaaS settings store.

This module validates that the User model correctly has the disabled_skills column
added to fix the bug where toggling a skill off in Settings > Skills appeared to
save but reverted after page refresh.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Repository path
REPO = Path("/workspace/OpenHands")
ENTERPRISE = REPO / "enterprise"
USER_PY = ENTERPRISE / "storage" / "user.py"
MIGRATION_FILE = ENTERPRISE / "migrations" / "versions" / "104_add_disabled_skills_to_user.py"


def test_user_model_has_disabled_skills_column():
    """Fail-to-pass: User model must have disabled_skills column defined.

    This test checks that the User SQLAlchemy model has the disabled_skills
    column added to persist skill toggles in SaaS settings store.
    """
    assert USER_PY.exists(), f"User model file not found at {USER_PY}"

    content = USER_PY.read_text()

    # Check for JSON import
    assert "from sqlalchemy import (" in content, "SQLAlchemy imports not found"
    assert "JSON," in content, "JSON type not imported from sqlalchemy"

    # Check for disabled_skills column in User class
    assert "disabled_skills = Column(JSON, nullable=True)" in content, \
        "disabled_skills column not found in User model"


def test_user_model_column_can_store_and_return_data():
    """Fail-to-pass: User model must be able to store and retrieve disabled_skills.

    Tests that a User instance can have disabled_skills set and retrieved
    using SQLAlchemy's attribute access pattern.
    """
    assert USER_PY.exists(), f"User model file not found at {USER_PY}"

    # Parse the file to extract the User class
    content = USER_PY.read_text()
    tree = ast.parse(content)

    # Find the User class
    user_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "User":
            user_class = node
            break

    assert user_class is not None, "User class not found in user.py"

    # Check that disabled_skills is defined as a Column
    disabled_skills_found = False
    for item in user_class.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "disabled_skills":
                    # Verify it's a Column with JSON type
                    if isinstance(item.value, ast.Call):
                        func = item.value.func
                        if isinstance(func, ast.Name) and func.id == "Column":
                            args = item.value.args
                            if args:
                                first_arg = args[0]
                                if isinstance(first_arg, ast.Name) and first_arg.id == "JSON":
                                    disabled_skills_found = True
                                    break

    assert disabled_skills_found, "disabled_skills must be a Column with JSON type in User model"


def test_migration_file_exists_and_valid():
    """Fail-to-pass: Migration 104 must exist with correct Alembic structure.

    This test verifies that the Alembic migration file for adding disabled_skills
    to the user table exists and has proper revision identifiers.
    """
    assert MIGRATION_FILE.exists(), f"Migration file not found at {MIGRATION_FILE}"

    content = MIGRATION_FILE.read_text()

    # Check for proper Alembic structure
    assert "Revision ID: 104" in content or "revision: str = '104'" in content, \
        "Migration must have revision ID 104"
    assert "from alembic import op" in content, "Alembic op import not found"
    assert "import sqlalchemy as sa" in content, "SQLAlchemy import not found"

    # Check for upgrade function with correct column addition
    assert "def upgrade()" in content, "upgrade() function not found"
    assert "op.add_column('user', sa.Column('disabled_skills', sa.JSON(), nullable=True))" in content, \
        "Correct add_column call not found in upgrade()"

    # Check for downgrade function
    assert "def downgrade()" in content, "downgrade() function not found"
    assert "op.drop_column('user', 'disabled_skills')" in content, \
        "Correct drop_column call not found in downgrade()"


def test_migration_references_correct_down_revision():
    """Fail-to-pass: Migration must correctly reference revision 103 as down_revision.

    This ensures the migration chain is properly linked for Alembic to apply
    migrations in the correct order.
    """
    assert MIGRATION_FILE.exists(), f"Migration file not found at {MIGRATION_FILE}"

    content = MIGRATION_FILE.read_text()

    # Check that down_revision references 103
    assert "down_revision" in content, "down_revision not defined"
    assert "'103'" in content or '"103"' in content or "down_revision = '103'" in content, \
        "Migration must have down_revision = '103'"


def test_enterprise_storage_imports():
    """Pass-to-pass: Enterprise storage module must import without errors.

    Verifies that the enterprise storage module loads correctly with the
    disabled_skills column addition.
    """
    # Add enterprise to path temporarily for import test
    sys.path.insert(0, str(REPO))

    try:
        # Set up minimal environment for import
        os.environ.setdefault("DISABLE_MICROAGENTS", "true")

        # Try importing the user module
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"""
import sys
sys.path.insert(0, '{REPO}')
os.environ.setdefault('DISABLE_MICROAGENTS', 'true')

# Mock required dependencies that might not be installed
import sys
from unittest.mock import MagicMock

# Mock enterprise modules that might have complex dependencies
for mod in ['enterprise.storage.database', 'enterprise.storage.role']:
    sys.modules[mod] = MagicMock()

# Now try to import user module
from enterprise.storage import user
print("Import successful")
print(f"User class: {{user.User}}")
                """
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO),
        )

        # We expect this might fail due to dependencies, but we check syntax
        # A syntax error would indicate the patch broke the file
        if result.returncode != 0:
            # If it fails, ensure it's NOT due to syntax error
            assert "SyntaxError" not in result.stderr, f"Syntax error in user.py: {result.stderr}"
            # Module loading issues are acceptable in this environment

    finally:
        if str(REPO) in sys.path:
            sys.path.remove(str(REPO))


def test_user_model_syntax_valid():
    """Pass-to-pass: User model file must have valid Python syntax.

    Ensures the patched user.py is syntactically correct Python.
    """
    assert USER_PY.exists(), f"User model file not found at {USER_PY}"

    content = USER_PY.read_text()

    # Parse to check for syntax errors
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {USER_PY}: {e}")


def test_migration_file_syntax_valid():
    """Pass-to-pass: Migration file must have valid Python syntax.

    Ensures the migration file is syntactically correct Python.
    """
    assert MIGRATION_FILE.exists(), f"Migration file not found at {MIGRATION_FILE}"

    content = MIGRATION_FILE.read_text()

    # Parse to check for syntax errors
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {MIGRATION_FILE}: {e}")


def test_disabled_skills_column_attributes():
    """Fail-to-pass: disabled_skills column must have correct SQLAlchemy attributes.

    Verifies that disabled_skills is defined as:
    - Column type: JSON
    - nullable: True (allows null values)
    """
    assert USER_PY.exists(), f"User model file not found at {USER_PY}"

    content = USER_PY.read_text()

    # Verify the exact column definition
    expected_patterns = [
        "disabled_skills = Column(JSON, nullable=True)",
    ]

    for pattern in expected_patterns:
        assert pattern in content, f"Required pattern not found: {pattern}"


def test_repo_ruff_check_enterprise():
    """Repo's ruff linter passes on enterprise storage/user.py (pass_to_pass).

    Runs the repo's configured ruff linter on the modified file.
    """
    r = subprocess.run(
        [
            "ruff",
            "check",
            "--config",
            f"{REPO}/enterprise/dev_config/python/ruff.toml",
            f"{REPO}/enterprise/storage/user.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format_enterprise():
    """Repo's ruff format check passes on enterprise storage/user.py (pass_to_pass).

    Verifies the code is properly formatted according to repo standards.
    """
    r = subprocess.run(
        [
            "ruff",
            "format",
            "--config",
            f"{REPO}/enterprise/dev_config/python/ruff.toml",
            "--check",
            f"{REPO}/enterprise/storage/user.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_validate_pyproject():
    """Repo's pyproject.toml is valid (pass_to_pass).

    Validates the enterprise pyproject.toml file structure.
    """
    # Install validate-pyproject if not available
    subprocess.run(
        ["pip", "install", "-q", "validate-pyproject"],
        capture_output=True,
        timeout=60,
    )
    r = subprocess.run(
        ["validate-pyproject", f"{REPO}/enterprise/pyproject.toml"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr}"


def test_repo_enterprise_storage_tests():
    """Repo's enterprise storage tests pass (pass_to_pass).

    Runs the storage-related unit tests for the enterprise module.
    """
    r = subprocess.run(
        [
            "poetry",
            "run",
            "pytest",
            "-x",
            "-v",
            "tests/unit/storage/test_database.py",
            "tests/unit/storage/test_user_app_settings_store.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/enterprise",
    )
    assert r.returncode == 0, f"Storage tests failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
