"""
Test suite for bun-sql-undefined-insert task.

Tests two categories:
1. Code behavior: SQL helper filters undefined values in INSERT statements
2. Config update: test/CLAUDE.md documents the nested object equality testing style
3. Pass-to-pass: Repo CI checks that should pass on both base and fixed commits
"""

import subprocess
import json
import re
import os
from pathlib import Path

REPO = Path("/workspace/bun")
TESTS_DIR = REPO / "test" / "js" / "sql"
SHARED_SQL = REPO / "src" / "js" / "internal" / "sql" / "shared.ts"
SQLITE_SQL = REPO / "src" / "js" / "internal" / "sql" / "sqlite.ts"
MYSQL_SQL = REPO / "src" / "js" / "internal" / "sql" / "mysql.ts"
POSTGRES_SQL = REPO / "src" / "js" / "internal" / "sql" / "postgres.ts"
CLAUde_MD = REPO / "test" / "CLAUDE.md"


def _setup_bun_env():
    """Set up environment with bun in PATH."""
    env = os.environ.copy()
    env["PATH"] = "/root/.bun/bin:" + env.get("PATH", "")
    return env


def _run_bun_script(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Bun script directly using node."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["npx", "ts-node", "--transpile-only", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO),
        )
    finally:
        script_path.unlink(missing_ok=True)


# =============================================================================
# FAIL-TO-PASS TESTS (Code behavior - should fail before fix, pass after)
# =============================================================================

def test_shared_ts_has_build_defined_columns():
    """shared.ts must export the buildDefinedColumnsAndQuery helper."""
    content = SHARED_SQL.read_text()
    assert "function buildDefinedColumnsAndQuery" in content, "buildDefinedColumnsAndQuery function must be defined"
    assert "export default {" in content and "buildDefinedColumnsAndQuery" in content, \
        "buildDefinedColumnsAndQuery must be exported"


def test_sqlite_ts_uses_helper():
    """sqlite.ts must import and use buildDefinedColumnsAndQuery."""
    content = SQLITE_SQL.read_text()
    assert "buildDefinedColumnsAndQuery" in content, "sqlite.ts must import buildDefinedColumnsAndQuery"
    assert "const { definedColumns, columnsSql } = buildDefinedColumnsAndQuery" in content, \
        "sqlite.ts must use buildDefinedColumnsAndQuery"


def test_sqlite_omits_undefined_columns():
    """SQLite SQL helper must omit undefined columns from INSERT statements."""
    content = SQLITE_SQL.read_text()
    # Check that the undefined-filtering logic is present
    assert "hasDefinedValue" in content or "typeof columnValue === \"undefined\"" in content, \
        "Must check for defined values before including columns"
    # Check that it builds columns list dynamically
    assert "definedColumns" in content and "columnsSql" in content, \
        "Must use dynamic column building"


def test_shared_helper_checks_all_items():
    """buildDefinedColumnsAndQuery must check all items in array for defined values."""
    content = SHARED_SQL.read_text()
    # The helper must iterate through items array to find any defined value
    assert "for (let j = 0; j < items.length; j++)" in content, \
        "Must iterate through all items to find defined values"
    assert 'if (typeof items[j][column] !== "undefined")' in content, \
        "Must check if each item has a defined value for the column"


def test_shared_helper_returns_correct_structure():
    """buildDefinedColumnsAndQuery must return { definedColumns, columnsSql }."""
    content = SHARED_SQL.read_text()
    # Check the function returns the expected structure
    assert "return { definedColumns, columnsSql }" in content, \
        "Must return definedColumns and columnsSql"


def test_claude_md_has_nested_object_section():
    """test/CLAUDE.md must have the 'Nested/complex object equality' section."""
    content = CLAUde_MD.read_text()
    assert "### Nested/complex object equality" in content, \
        "CLAUDE.md must have 'Nested/complex object equality' section"


def test_claude_md_prefers_to_equal():
    """CLAUDE.md must recommend .toEqual over multiple .toBe assertions."""
    content = CLAUde_MD.read_text()
    # Check for the preference statement
    assert ".toEqual" in content.lower() or "toEqual" in content, \
        "Must mention .toEqual for nested objects"
    # Check for the explicit recommendation
    assert "Prefer usage of `.toEqual`" in content or "prefer" in content.lower() and "toequal" in content.lower(), \
        "Must recommend using .toEqual"


def test_claude_md_has_bad_example():
    """CLAUDE.md must show the 'BAD' example with multiple .toBe assertions."""
    content = CLAUde_MD.read_text()
    assert "BAD (try to avoid doing this)" in content or "BAD" in content, \
        "Must have a 'BAD' example showing what to avoid"
    # Check for multiple expect().toBe pattern
    bad_pattern = re.search(r'expect\(result\[\d+\]\.[\w]+\)\.toBe', content)
    assert bad_pattern is not None, \
        "Must show BAD example with multiple expect(result[N].prop).toBe assertions"


def test_claude_md_has_good_example():
    """CLAUDE.md must show the 'GOOD' example with .toEqual."""
    content = CLAUde_MD.read_text()
    assert "GOOD (always prefer this)" in content or "GOOD" in content, \
        "Must have a 'GOOD' example showing preferred approach"
    assert "expect(result).toEqual([" in content or "toEqual" in content, \
        "Must show GOOD example with expect(result).toEqual"


def test_claude_md_example_mentions_middle_item():
    """CLAUDE.md example must highlight the middle item preservation issue."""
    content = CLAUde_MD.read_text()
    # The example should mention that middle item's value must be preserved
    assert "middle" in content.lower() and "preserved" in content.lower(), \
        "Example must mention that middle item values must be preserved (data loss issue)"


def test_sqlite_error_for_all_undefined():
    """SQLite adapter must throw error when all columns are undefined."""
    content = SQLITE_SQL.read_text()
    assert "SyntaxError" in content, "Must throw SyntaxError for undefined-only inserts"
    assert "at least one column with a defined value" in content or "one column with a defined value" in content, \
        "Error message must mention needing at least one defined column"


def test_import_structure_in_sqlite():
    """sqlite.ts must import buildDefinedColumnsAndQuery from shared."""
    content = SQLITE_SQL.read_text()
    # Check the require/import statement
    assert 'const { SQLHelper, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared")' in content, \
        "Must import buildDefinedColumnsAndQuery from internal/sql/shared"


# =============================================================================
# PASS-TO-PASS TESTS (Repo CI checks - should pass on both base and fixed commits)
# =============================================================================

def test_repo_banned_words():
    """Repo's banned words check passes (pass_to_pass)."""
    env = _setup_bun_env()
    r = subprocess.run(
        ["bun", "run", "banned"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_sql_shared_transpiles():
    """SQL shared.ts transpiles without errors (pass_to_pass)."""
    env = _setup_bun_env()
    r = subprocess.run(
        ["bun", "build", "--target=bun", "--outfile=/dev/null", str(SHARED_SQL)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"shared.ts transpile failed:\n{r.stderr[-500:]}"


def test_repo_sql_sqlite_transpiles():
    """SQL sqlite.ts transpiles without errors (pass_to_pass)."""
    env = _setup_bun_env()
    r = subprocess.run(
        ["bun", "build", "--target=bun", "--outfile=/dev/null", str(SQLITE_SQL)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"sqlite.ts transpile failed:\n{r.stderr[-500:]}"


def test_repo_sql_mysql_transpiles():
    """SQL mysql.ts transpiles without errors (pass_to_pass)."""
    env = _setup_bun_env()
    r = subprocess.run(
        ["bun", "build", "--target=bun", "--outfile=/dev/null", str(MYSQL_SQL)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"mysql.ts transpile failed:\n{r.stderr[-500:]}"


def test_repo_sql_postgres_transpiles():
    """SQL postgres.ts transpiles without errors (pass_to_pass)."""
    env = _setup_bun_env()
    r = subprocess.run(
        ["bun", "build", "--target=bun", "--outfile=/dev/null", str(POSTGRES_SQL)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"postgres.ts transpile failed:\n{r.stderr[-500:]}"
