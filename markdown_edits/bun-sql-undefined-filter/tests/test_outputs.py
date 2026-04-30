"""
Test suite for Bun SQL undefined filter task.

Tests verify:
1. Code changes: buildDefinedColumnsAndQuery function exists in shared.ts
2. Config update: test/CLAUDE.md contains the nested/complex object equality section
3. The SQL adapters use the new function
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/bun")

def test_shared_ts_has_build_defined_columns():
    """FAIL_TO_PASS: shared.ts must contain buildDefinedColumnsAndQuery function."""
    shared_ts = REPO / "src/js/internal/sql/shared.ts"
    content = shared_ts.read_text()

    # The function must exist
    assert "function buildDefinedColumnsAndQuery" in content, \
        "shared.ts must contain buildDefinedColumnsAndQuery function"

    # It should be exported
    assert "buildDefinedColumnsAndQuery," in content, \
        "buildDefinedColumnsAndQuery must be exported from shared.ts"

def test_sqlite_ts_uses_new_function():
    """FAIL_TO_PASS: sqlite.ts must import and use buildDefinedColumnsAndQuery."""
    sqlite_ts = REPO / "src/js/internal/sql/sqlite.ts"
    content = sqlite_ts.read_text()

    # Must import the function
    assert "buildDefinedColumnsAndQuery" in content, \
        "sqlite.ts must import buildDefinedColumnsAndQuery from shared"

    # Must call the function in INSERT handling
    assert "buildDefinedColumnsAndQuery(" in content, \
        "sqlite.ts must call buildDefinedColumnsAndQuery for INSERT handling"

    # Must use definedColumns (not columnCount) for iteration
    assert "definedColumnCount" in content, \
        "sqlite.ts must use definedColumnCount for column iteration"

def test_postgres_ts_uses_new_function():
    """FAIL_TO_PASS: postgres.ts must import and use buildDefinedColumnsAndQuery."""
    postgres_ts = REPO / "src/js/internal/sql/postgres.ts"
    content = postgres_ts.read_text()

    assert "buildDefinedColumnsAndQuery" in content, \
        "postgres.ts must import buildDefinedColumnsAndQuery from shared"
    assert "buildDefinedColumnsAndQuery(" in content, \
        "postgres.ts must call buildDefinedColumnsAndQuery for INSERT handling"
    assert "definedColumnCount" in content, \
        "postgres.ts must use definedColumnCount for column iteration"

def test_mysql_ts_uses_new_function():
    """FAIL_TO_PASS: mysql.ts must import and use buildDefinedColumnsAndQuery."""
    mysql_ts = REPO / "src/js/internal/sql/mysql.ts"
    content = mysql_ts.read_text()

    assert "buildDefinedColumnsAndQuery" in content, \
        "mysql.ts must import buildDefinedColumnsAndQuery from shared"
    assert "buildDefinedColumnsAndQuery(" in content, \
        "mysql.ts must call buildDefinedColumnsAndQuery for INSERT handling"
    assert "definedColumnCount" in content, \
        "mysql.ts must use definedColumnCount for column iteration"

def test_claude_md_has_object_equality_section():
    """FAIL_TO_PASS: test/CLAUDE.md must have nested/complex object equality section."""
    claude_md = REPO / "test/CLAUDE.md"
    content = claude_md.read_text()

    # Check for the section header
    assert "Nested/complex object equality" in content, \
        "CLAUDE.md must have 'Nested/complex object equality' section"

    # Check for the example of using toEqual
    assert "Prefer usage of `.toEqual`" in content, \
        "CLAUDE.md must document preferring toEqual for nested objects"

    # Check for the example showing the BAD pattern
    assert "BAD (try to avoid doing this)" in content, \
        "CLAUDE.md must show the BAD pattern example"

    # Check for the example showing the GOOD pattern
    assert "GOOD (always prefer this)" in content, \
        "CLAUDE.md must show the GOOD pattern example with toEqual"

def test_claude_md_has_fixed_promise_with_resolvers():
    """FAIL_TO_PASS: test/CLAUDE.md Promise.withResolvers example must have type annotation."""
    claude_md = REPO / "test/CLAUDE.md"
    content = claude_md.read_text()

    # The fix adds <void> type annotation to Promise.withResolvers
    assert "Promise.withResolvers<void>()" in content, \
        "CLAUDE.md must show Promise.withResolvers with type annotation <void>()"

def test_build_defined_columns_logic_correct():
    """FAIL_TO_PASS: buildDefinedColumnsAndQuery must correctly filter undefined columns."""
    shared_ts = REPO / "src/js/internal/sql/shared.ts"
    content = shared_ts.read_text()

    # Find the function and check its logic
    func_start = content.find("function buildDefinedColumnsAndQuery")
    func_end = content.find("const SQLITE_MEMORY", func_start)
    func_content = content[func_start:func_end]

    # Must check for undefined using typeof
    assert 'typeof items[j][column] !== "undefined"' in func_content, \
        "Must check typeof !== 'undefined' to detect defined values"

    # Must iterate through array items when checking
    assert "for (let j = 0; j < items.length; j++)" in func_content, \
        "Must iterate through all items in array to find defined values"

    # Must handle single item case too
    assert "hasDefinedValue = typeof items[column] !== \"undefined\"" in func_content, \
        "Must handle single item case (non-array)"

def test_error_message_for_empty_columns():
    """FAIL_TO_PASS: Must throw SyntaxError when all columns are undefined."""
    # Check all three adapters
    for adapter in ["sqlite.ts", "postgres.ts", "mysql.ts"]:
        adapter_path = REPO / "src/js/internal/sql" / adapter
        content = adapter_path.read_text()

        assert 'throw new SyntaxError("Insert needs to have at least one column with a defined value")' in content, \
            f"{adapter} must throw SyntaxError when no columns have defined values"

def test_type_script_compiles():
    """PASS_TO_PASS: TypeScript files must have valid syntax."""
    # Use bun to check TypeScript syntax
    for ts_file in ["shared.ts", "sqlite.ts", "postgres.ts", "mysql.ts"]:
        ts_path = REPO / "src/js/internal/sql" / ts_file
        result = subprocess.run(
            ["bun", "--check", str(ts_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Note: bun --check may have some errors due to internal module paths
        # but it will catch syntax errors
        assert result.returncode == 0 or "error:" not in result.stderr.lower(), \
            f"{ts_file} must have valid TypeScript syntax: {result.stderr}"
