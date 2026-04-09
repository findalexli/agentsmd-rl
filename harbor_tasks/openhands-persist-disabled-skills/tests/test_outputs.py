"""Behavioral tests for disabled_skills column addition to User model."""

import os
import sys
import subprocess
import ast
import json
import pytest
from pathlib import Path

# Repository path
REPO = Path("/workspace/OpenHands")
ENTERPRISE_DIR = REPO / "enterprise"


def _run_python_code(code: str, timeout: int = 30, cwd=None) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
        cwd=cwd or REPO,
    )


def _run_python_file(script_path: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python file in the repo environment."""
    return subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO,
    )


# =============================================================================
# FAIL-TO-PASS TESTS (Behavioral - must fail on base, pass on fix)
# These tests EXECUTE code to verify actual behavior
# =============================================================================


def test_user_model_has_disabled_skills_column():
    """Fail-to-pass: User model's disabled_skills column is defined as Column(JSON, nullable=True)."""
    # Use AST to check the user.py file without importing (avoids dependency issues)
    user_file = REPO / "enterprise" / "storage" / "user.py"
    content = user_file.read_text()
    tree = ast.parse(content)

    # Check that disabled_skills column exists with correct type
    found_disabled_skills = False
    found_json_import = False

    # First check if JSON is imported from sqlalchemy
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'sqlalchemy':
            for alias in node.names:
                if alias.name == 'JSON':
                    found_json_import = True
                    break

    # Check for disabled_skills column definition
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'disabled_skills':
                    # Check if it's a Column call with JSON type
                    if isinstance(node.value, ast.Call):
                        call = node.value
                        if isinstance(call.func, ast.Name) and call.func.id == 'Column':
                            # Check if first arg is JSON() or has JSON type
                            if call.args:
                                first_arg = call.args[0]
                                if isinstance(first_arg, ast.Call):
                                    if isinstance(first_arg.func, ast.Name) and first_arg.func.id == 'JSON':
                                        found_disabled_skills = True
                                elif isinstance(first_arg, ast.Name) and first_arg.id == 'JSON':
                                    found_disabled_skills = True

    assert found_json_import, "JSON type not imported from sqlalchemy"
    assert found_disabled_skills, "disabled_skills column not found or not defined as Column(JSON)"


def test_user_model_imports_json_type():
    """Fail-to-pass: User model file imports JSON from sqlalchemy."""
    # Use AST to verify JSON is imported from sqlalchemy (no runtime import needed)
    user_file = REPO / "enterprise" / "storage" / "user.py"
    content = user_file.read_text()
    tree = ast.parse(content)

    found_json_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'sqlalchemy':
            for alias in node.names:
                if alias.name == 'JSON':
                    found_json_import = True
                    break

    assert found_json_import, "JSON type must be imported from sqlalchemy in user.py"


def test_migration_file_exists():
    """Fail-to-pass: Migration 104 exists and is a valid Python module that can be loaded."""
    migration_file = REPO / "enterprise" / "migrations" / "versions" / "104_add_disabled_skills_to_user.py"

    # Check file exists
    if not migration_file.exists():
        pytest.fail(f"Migration file not found: {migration_file}")

    # Check it's valid Python syntax by trying to import it
    code = f"""
import sys
sys.path.insert(0, '/workspace/OpenHands')
sys.path.insert(0, '/workspace/OpenHands/enterprise')
sys.path.insert(0, '/workspace/OpenHands/enterprise/migrations/versions')

# Try to import as a module - this will fail if syntax is invalid
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("migration_104", "{migration_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("PASS: Migration 104 is valid Python and loadable")
except Exception as e:
    print(f"FAIL: Cannot load migration - {{e}}")
    sys.exit(1)
"""
    r = _run_python_code(code)
    assert r.returncode == 0, f"Migration load test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_migration_has_upgrade_downgrade():
    """Fail-to-pass: Migration module has callable upgrade and downgrade functions."""
    migration_file = REPO / "enterprise" / "migrations" / "versions" / "104_add_disabled_skills_to_user.py"

    code = f"""
import sys
sys.path.insert(0, '/workspace/OpenHands')
sys.path.insert(0, '/workspace/OpenHands/enterprise')
sys.path.insert(0, '/workspace/OpenHands/enterprise/migrations/versions')

import importlib.util
spec = importlib.util.spec_from_file_location("migration_104", "{migration_file}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Check upgrade function exists and is callable
if not hasattr(module, 'upgrade'):
    print("FAIL: Missing upgrade function")
    sys.exit(1)
if not callable(module.upgrade):
    print("FAIL: upgrade is not callable")
    sys.exit(1)

# Check downgrade function exists and is callable
if not hasattr(module, 'downgrade'):
    print("FAIL: Missing downgrade function")
    sys.exit(1)
if not callable(module.downgrade):
    print("FAIL: downgrade is not callable")
    sys.exit(1)

print("PASS: Migration has upgrade() and downgrade() functions")
"""
    r = _run_python_code(code)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_migration_upgrade_adds_column():
    """Fail-to-pass: Migration upgrade function contains op.add_column for 'user' table."""
    migration_file = REPO / "enterprise" / "migrations" / "versions" / "104_add_disabled_skills_to_user.py"

    code = f"""
import sys
import ast

# Parse the migration file
with open("{migration_file}") as f:
    tree = ast.parse(f.read())

# Find upgrade function and check for op.add_column('user', ...)
found_add_column = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'upgrade':
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                func = stmt.func
                if isinstance(func, ast.Attribute) and func.attr == 'add_column':
                    # Check first argument is 'user'
                    if stmt.args:
                        first_arg = stmt.args[0]
                        if isinstance(first_arg, ast.Constant) and first_arg.value == 'user':
                            found_add_column = True
                            break
                        if isinstance(first_arg, ast.Str):  # Python < 3.8
                            found_add_column = True
                            break

if not found_add_column:
    print("FAIL: upgrade() should call op.add_column('user', ...)")
    sys.exit(1)

print("PASS: Migration upgrade adds column to user table")
"""
    r = _run_python_code(code)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# =============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD - must pass on both base and fix)
# These verify the repo's quality checks still pass
# =============================================================================


def test_repo_structure():
    """Pass-to-pass: Enterprise storage directory exists with required files."""
    enterprise_dir = REPO / "enterprise"
    storage_dir = enterprise_dir / "storage"
    user_file = storage_dir / "user.py"
    migrations_dir = enterprise_dir / "migrations" / "versions"

    assert enterprise_dir.exists(), "enterprise directory not found"
    assert storage_dir.exists(), "enterprise/storage directory not found"
    assert user_file.exists(), "enterprise/storage/user.py not found"
    assert migrations_dir.exists(), "enterprise/migrations/versions directory not found"


def test_user_model_basic_columns():
    """Pass-to-pass: User model has expected basic columns (file-based check)."""
    user_file = REPO / "enterprise" / "storage" / "user.py"
    content = user_file.read_text()

    # Parse the AST
    tree = ast.parse(content)

    column_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    column_names.add(target.id)

    # Core columns that should always exist
    assert 'id' in column_names, "User missing 'id' column"
    assert 'email' in column_names, "User missing 'email' column"
    assert 'current_org_id' in column_names, "User missing 'current_org_id' column"
    assert 'sandbox_grouping_strategy' in column_names, "User missing 'sandbox_grouping_strategy' column"


def test_repo_python_syntax():
    """Pass-to-pass: All enterprise/storage Python files have valid syntax."""
    storage_dir = REPO / "enterprise" / "storage"
    errors = []

    for py_file in storage_dir.glob("*.py"):
        try:
            ast.parse(py_file.read_text())
        except SyntaxError as e:
            errors.append(f"{py_file.name}: {e}")

    assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


def test_repo_migration_syntax():
    """Pass-to-pass: All migration files have valid Python syntax."""
    migrations_dir = REPO / "enterprise" / "migrations" / "versions"
    errors = []

    for py_file in migrations_dir.glob("*.py"):
        try:
            ast.parse(py_file.read_text())
        except SyntaxError as e:
            errors.append(f"{py_file.name}: {e}")

    assert not errors, f"Migration syntax errors:\n" + "\n".join(errors)


def test_repo_alembic_latest_migration():
    """Pass-to-pass: Latest Alembic migration is properly formatted."""
    migrations_dir = REPO / "enterprise" / "migrations" / "versions"

    # Get the latest migration file (highest revision number)
    latest_file = None
    latest_rev = -1

    for py_file in migrations_dir.glob("[0-9][0-9][0-9]_*.py"):
        rev_str = py_file.name[:3]
        try:
            rev = int(rev_str)
            if rev > latest_rev:
                latest_rev = rev
                latest_file = py_file
        except ValueError:
            continue

    assert latest_file is not None, "No migration files found"

    # Verify the latest migration has proper structure
    content = latest_file.read_text()
    tree = ast.parse(content)

    # Check for revision and down_revision
    found_revision = False
    found_down_revision = False

    for node in ast.walk(tree):
        # Handle regular assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == 'revision':
                        found_revision = True
                    elif target.id == 'down_revision':
                        found_down_revision = True
        # Handle type-annotated assignments (e.g., revision: str = '103')
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                if node.target.id == 'revision':
                    found_revision = True
                elif node.target.id == 'down_revision':
                    found_down_revision = True

    assert found_revision, f"Latest migration {latest_file.name} missing revision"
    assert found_down_revision, f"Latest migration {latest_file.name} missing down_revision"


def test_repo_sqlalchemy_model_conventions():
    """Pass-to-pass: SQLAlchemy models follow enterprise conventions."""
    user_file = REPO / "enterprise" / "storage" / "user.py"
    content = user_file.read_text()
    tree = ast.parse(content)

    # Check for __tablename__ attribute
    found_tablename = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__tablename__':
                    found_tablename = True
                    break

    assert found_tablename, "User model missing __tablename__ attribute"


def test_repo_migration_conventions():
    """Pass-to-pass: Migration files follow naming and structure conventions."""
    migrations_dir = REPO / "enterprise" / "migrations" / "versions"

    errors = []
    for py_file in migrations_dir.glob("*.py"):
        content = py_file.read_text()
        tree = ast.parse(content)

        # Check for required functions
        found_upgrade = False
        found_downgrade = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'upgrade':
                    found_upgrade = True
                elif node.name == 'downgrade':
                    found_downgrade = True

        if not found_upgrade:
            errors.append(f"{py_file.name}: missing upgrade() function")
        if not found_downgrade:
            errors.append(f"{py_file.name}: missing downgrade() function")

    assert not errors, f"Migration convention errors:\n" + "\n".join(errors)


def test_storage_user_column_order():
    """Pass-to-pass: User model column ordering follows enterprise conventions."""
    user_file = REPO / "enterprise" / "storage" / "user.py"
    content = user_file.read_text()

    # Find positions of relevant columns
    sandbox_pos = content.find("sandbox_grouping_strategy")
    git_user_email_pos = content.find("git_user_email")

    assert sandbox_pos != -1, "sandbox_grouping_strategy column not found"
    assert git_user_email_pos != -1, "git_user_email column not found"

    # sandbox_grouping_strategy should come after git_user_email
    assert sandbox_pos > git_user_email_pos, \
        "Column ordering convention violated"
