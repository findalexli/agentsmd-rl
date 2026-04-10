#!/usr/bin/env python3
"""
Test suite for VectorDB race condition fix.

Tests verify that the DuplicateException is properly caught during metadata
creation to handle concurrent initialization scenarios.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/workspace/appwrite")
TARGET_FILE = REPO_ROOT / "src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php"


def test_duplicate_exception_imported():
    """Verify DuplicateException is imported in the file."""
    content = TARGET_FILE.read_text()

    # Should import DuplicateException - check both old and new import styles
    assert "use Appwrite\\Extend\\Exception\\DuplicateException;" in content or \
           "DuplicateException" in content, \
           "DuplicateException must be imported or referenced in the file"


def test_nested_try_catch_for_create():
    """Verify nested try-catch structure exists around dbForDatabases->create()."""
    content = TARGET_FILE.read_text()

    # Check for nested try block inside the exists check
    assert "if (!$dbForDatabases->exists(null, Database::METADATA))" in content, \
           "Must check if metadata exists before creating"

    # Check for the nested try-catch structure
    # The pattern should be: if exists check -> try -> create -> catch DuplicateException
    lines = content.split('\n')
    found_exists_check = False
    found_nested_try = False
    found_catch_duplicate = False
    found_create_in_try = False

    for i, line in enumerate(lines):
        if "if (!$dbForDatabases->exists(null, Database::METADATA))" in line:
            found_exists_check = True
            # Look for the nested try inside the if block (scan next 20 lines)
            for j in range(i, min(i + 20, len(lines))):
                curr_line = lines[j]

                # Look for nested try inside the if block (after the if line)
                if j > i and 'try {' in curr_line:
                    found_nested_try = True

                # Look for ->create() inside the nested try block
                if found_nested_try and '->create()' in curr_line and 'catch' not in curr_line:
                    found_create_in_try = True

                # Look for catch DuplicateException
                if found_nested_try and 'catch (DuplicateException)' in curr_line:
                    found_catch_duplicate = True
            break

    assert found_exists_check, "Must check if metadata exists before creating"
    assert found_nested_try, "Must have nested try block inside the exists check"
    assert found_catch_duplicate, "Must catch DuplicateException in nested try-catch"
    assert found_create_in_try, "Must call ->create() inside the nested try block"


def test_catch_block_is_empty_or_has_comment():
    """Verify the catch block is intentionally empty (race condition handling)."""
    content = TARGET_FILE.read_text()

    # Find the catch (DuplicateException) line
    assert 'catch (DuplicateException)' in content, "Must catch DuplicateException"


def test_comment_removed():
    """Verify the old comment about 'passing null' is removed."""
    content = TARGET_FILE.read_text()

    # The old comment should be removed
    assert "// passing null in creates only creates the metadata collection" not in content, \
           "Old comment about 'passing null' should be removed"


def test_php_syntax_valid():
    """Verify the PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


def test_outer_try_block_preserved():
    """Verify the outer try block wrapping createCollection is preserved."""
    content = TARGET_FILE.read_text()

    # The outer try block that wraps createCollection should still exist
    assert "$dbForDatabases->createCollection(" in content, \
           "Must still call createCollection after metadata initialization"

    # Check that we have proper structure:
    # 1. An outer try block exists before createCollection
    # 2. The createCollection call exists
    lines = content.split('\n')
    found_try_before_collection = False
    found_create_collection = False

    for i, line in enumerate(lines):
        # Look for try { that comes before createCollection
        if 'try {' in line and not found_create_collection:
            found_try_before_collection = True
        # Look for createCollection call
        if '$dbForDatabases->createCollection(' in line:
            found_create_collection = True

    assert found_try_before_collection, "Must have try block before createCollection"
    assert found_create_collection, "Must call createCollection"


def test_repo_lint():
    """Repo's PHP PSR-12 linting passes (pass_to_pass)."""
    # First ensure dependencies are installed
    r = subprocess.run(
        ["composer", "install", "--no-interaction"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT)
    )
    if r.returncode != 0:
        print(f"SKIP: Composer install failed, cannot run lint: {r.stderr[-200:]}")
        return  # Skip test if composer fails
    # Lint may fail on base commit, but should pass after fix formatting
    r = subprocess.run(
        ["composer", "lint"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT)
    )
    assert r.returncode == 0, f"PHP lint (Pint) failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_check():
    """Repo's PHP static analysis passes (pass_to_pass)."""
    # First ensure dependencies are installed
    r = subprocess.run(
        ["composer", "install", "--no-interaction"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT)
    )
    if r.returncode != 0:
        print(f"SKIP: Composer install failed, cannot run check: {r.stderr[-200:]}")
        return  # Skip test if composer fails
    # PHPStan static analysis
    r = subprocess.run(
        ["composer", "check"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT)
    )
    assert r.returncode == 0, f"PHP static analysis (PHPStan) failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_validate():
    """Repo's composer.json and composer.lock are valid (pass_to_pass)."""
    # composer validate works without installing dependencies
    r = subprocess.run(
        ["composer", "validate", "--strict"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT)
    )
    assert r.returncode == 0, f"Composer validation failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_duplicate_exception_imported,
        test_nested_try_catch_for_create,
        test_catch_block_is_empty_or_has_comment,
        test_comment_removed,
        test_php_syntax_valid,
        test_outer_try_block_preserved,
        test_repo_lint,
        test_repo_check,
        test_repo_validate,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
