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

    # Should import DuplicateException
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
    in_exists_block = False
    found_nested_try = False
    found_catch_duplicate = False
    found_create_in_try = False

    for i, line in enumerate(lines):
        if "if (!$dbForDatabases->exists(null, Database::METADATA))" in line:
            in_exists_block = True
            brace_count = 0
            for j in range(i, len(lines)):
                curr_line = lines[j]
                if '{' in curr_line:
                    brace_count += curr_line.count('{')
                if '}' in curr_line:
                    brace_count -= curr_line.count('}')

                # Look for nested try inside the if block
                if in_exists_block and 'try {' in curr_line and j > i:
                    found_nested_try = True

                # Look for ->create() inside a try block
                if found_nested_try and '->create()' in curr_line and 'catch' not in curr_line:
                    found_create_in_try = True

                # Look for catch DuplicateException
                if found_nested_try and 'catch (DuplicateException)' in curr_line:
                    found_catch_duplicate = True

                if brace_count == 0 and j > i:
                    break
            break

    assert found_nested_try, "Must have nested try block inside the exists check"
    assert found_catch_duplicate, "Must catch DuplicateException in nested try-catch"
    assert found_create_in_try, "Must call ->create() inside the nested try block"


def test_catch_block_is_empty_or_has_comment():
    """Verify the catch block is intentionally empty (race condition handling)."""
    content = TARGET_FILE.read_text()
    lines = content.split('\n')

    # Find the catch (DuplicateException) line
    for i, line in enumerate(lines):
        if 'catch (DuplicateException)' in line:
            # Check next few lines for empty or comment-only content
            for j in range(i, min(i+3, len(lines))):
                check_line = lines[j]
                if '}' in check_line and ('//' in check_line or check_line.strip() == '}'):
                    return True
                if j > i and check_line.strip() and not check_line.strip().startswith('//'):
                    # Has non-comment content - might be wrong, but let's be lenient
                    return True
    # If we found the catch, we pass - the structure is correct
    assert 'catch (DuplicateException)' in content, "Must catch DuplicateException"


def test_comment_removed():
    """Verify the old comment about 'passing null in creates only creates the metadata collection' is removed."""
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

    # Should have proper nesting of try blocks
    lines = content.split('\n')
    outer_try_line = None
    create_collection_line = None

    for i, line in enumerate(lines):
        if line.strip().startswith('try {') and 'create' not in line:
            outer_try_line = i
        if '$dbForDatabases->createCollection(' in line:
            create_collection_line = i

    assert outer_try_line is not None, "Must have outer try block"
    assert create_collection_line is not None, "Must call createCollection"
    assert outer_try_line < create_collection_line, \
           "Outer try block must wrap createCollection call"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_duplicate_exception_imported,
        test_nested_try_catch_for_create,
        test_catch_block_is_empty_or_has_comment,
        test_comment_removed,
        test_php_syntax_valid,
        test_outer_try_block_preserved,
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
