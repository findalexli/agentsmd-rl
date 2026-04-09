"""
Tests for migration utilities fix.

The PR fixes create_fks_for_table to gracefully handle pre-existing foreign keys.
Previously, only drop_fks_for_table handled pre-existing FKs. Now both utilities
use a new get_foreign_key_names helper.

Tests verify:
1. get_foreign_key_names returns FK names correctly
2. create_fks_for_table skips when FK already exists
3. The utilities work with the refactored code
"""

import os
import sys
import subprocess
from pathlib import Path

# Ensure the superset code is importable
REPO_ROOT = Path("/workspace/superset")
sys.path.insert(0, str(REPO_ROOT))

def test_get_foreign_key_names_function_exists():
    """Verify get_foreign_key_names function exists and is importable."""
    try:
        from superset.migrations.shared.utils import get_foreign_key_names
        assert callable(get_foreign_key_names), "get_foreign_key_names should be callable"
    except ImportError as e:
        raise AssertionError(
            "get_foreign_key_names function not found in superset.migrations.shared.utils. "
            "The PR should add this function."
        ) from e


def test_create_fks_for_table_has_existence_check():
    """Verify create_fks_for_table checks for pre-existing FKs before creating."""
    import inspect
    from superset.migrations.shared.utils import create_fks_for_table

    source = inspect.getsource(create_fks_for_table)

    # The fix should check if FK already exists using get_foreign_key_names
    assert "get_foreign_key_names" in source, (
        "create_fks_for_table should call get_foreign_key_names to check for pre-existing FKs"
    )
    assert "already exists" in source or "Skipping" in source, (
        "create_fks_for_table should have logic to skip when FK already exists"
    )


def test_drop_fks_for_table_uses_helper():
    """Verify drop_fks_for_table uses the new get_foreign_key_names helper."""
    import inspect
    from superset.migrations.shared.utils import drop_fks_for_table

    source = inspect.getsource(drop_fks_for_table)

    # After refactoring, should use get_foreign_key_names helper
    assert "get_foreign_key_names" in source, (
        "drop_fks_for_table should use get_foreign_key_names helper (refactored code)"
    )
    # Should NOT have the old inline implementation
    assert "inspector.get_foreign_keys" not in source, (
        "drop_fks_for_table should not inline the FK fetching logic (should use helper)"
    )


def test_get_foreign_key_names_has_proper_signature():
    """Verify get_foreign_key_names has proper function signature."""
    import inspect
    from superset.migrations.shared.utils import get_foreign_key_names

    sig = inspect.signature(get_foreign_key_names)
    params = list(sig.parameters.keys())

    assert "table_name" in params, (
        "get_foreign_key_names should have 'table_name' parameter"
    )

    # Check return type annotation
    assert sig.return_annotation == set[str] or "set" in str(sig.return_annotation), (
        f"get_foreign_key_names should return set[str], got {sig.return_annotation}"
    )


def test_get_foreign_key_names_has_docstring():
    """Verify get_foreign_key_names has a proper docstring."""
    from superset.migrations.shared.utils import get_foreign_key_names

    assert get_foreign_key_names.__doc__ is not None, (
        "get_foreign_key_names should have a docstring"
    )
    assert "foreign key" in get_foreign_key_names.__doc__.lower(), (
        "Docstring should mention foreign keys"
    )


def test_mypy_compliance_for_new_function():
    """Verify the new function has proper type hints (per agent config rules)."""
    import inspect
    from superset.migrations.shared.utils import get_foreign_key_names

    sig = inspect.signature(get_foreign_key_names)

    # All parameters should have type annotations
    for param_name, param in sig.parameters.items():
        assert param.annotation != inspect.Parameter.empty, (
            f"Parameter '{param_name}' should have type annotation (per project rules)"
        )

    # Return type should be annotated
    assert sig.return_annotation != inspect.Parameter.empty, (
        "get_foreign_key_names should have return type annotation"
    )


def test_syntax_validity():
    """Verify the modified file has valid Python syntax."""
    utils_file = REPO_ROOT / "superset" / "migrations" / "shared" / "utils.py"

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(utils_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, (
        f"utils.py has syntax errors:\n{result.stderr}"
    )


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD Checks
# These tests verify that the repo's existing CI checks pass on both
# the base commit AND after the fix is applied.
# =============================================================================

REPO = Path("/workspace/superset")


def test_repo_syntax_check():
    """Repo's Python syntax check passes (pass_to_pass)."""
    utils_file = REPO / "superset" / "migrations" / "shared" / "utils.py"
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(utils_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


def test_repo_ruff_lint():
    """Repo's ruff linting passes (pass_to_pass)."""
    # Ensure ruff is installed
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "superset/migrations/shared/utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_migrations_unit_tests():
    """Repo's migration utils unit tests pass (pass_to_pass)."""
    # Install test dependencies if needed
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest-mock", "cachetools", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Run the unit tests for migrations shared utils
    env = os.environ.copy()
    env["SUPERSET_SECRET_KEY"] = "test-secret-key"
    env["SUPERSET_TESTENV"] = "true"
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/unit_tests/migrations/shared/utils_test.py",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Migration unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_syntax_validity,
        test_get_foreign_key_names_function_exists,
        test_get_foreign_key_names_has_proper_signature,
        test_get_foreign_key_names_has_docstring,
        test_mypy_compliance_for_new_function,
        test_create_fks_for_table_has_existence_check,
        test_drop_fks_for_table_uses_helper,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
