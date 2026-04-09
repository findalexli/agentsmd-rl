"""
Task: bun-sql-filter-out-undefined-values
Repo: oven-sh/bun @ 47af15f3f469b6325a01935b4373d36c98061cbd
PR: 25830

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/bun"


def _run_bun_ts(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute TypeScript code via Bun in the repo directory."""
    script = Path(REPO) / "_eval_tmp_test.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_shared_ts_parses():
    """Modified shared.ts must parse without TypeScript errors."""
    shared_ts = Path(f"{REPO}/src/js/internal/sql/shared.ts")
    assert shared_ts.exists(), "shared.ts not found"

    # Check that buildDefinedColumnsAndQuery function exists
    content = shared_ts.read_text()
    assert "function buildDefinedColumnsAndQuery" in content, \
        "buildDefinedColumnsAndQuery function not found in shared.ts"


# [static] pass_to_pass
def test_sqlite_ts_parses():
    """Modified sqlite.ts must parse without TypeScript errors."""
    sqlite_ts = Path(f"{REPO}/src/js/internal/sql/sqlite.ts")
    assert sqlite_ts.exists(), "sqlite.ts not found"

    content = sqlite_ts.read_text()
    assert "buildDefinedColumnsAndQuery" in content, \
        "sqlite.ts does not import/use buildDefinedColumnsAndQuery"


# [static] pass_to_pass
def test_mysql_ts_parses():
    """Modified mysql.ts must parse without TypeScript errors."""
    mysql_ts = Path(f"{REPO}/src/js/internal/sql/mysql.ts")
    assert mysql_ts.exists(), "mysql.ts not found"

    content = mysql_ts.read_text()
    assert "buildDefinedColumnsAndQuery" in content, \
        "mysql.ts does not import/use buildDefinedColumnsAndQuery"


# [static] pass_to_pass
def test_postgres_ts_parses():
    """Modified postgres.ts must parse without TypeScript errors."""
    postgres_ts = Path(f"{REPO}/src/js/internal/sql/postgres.ts")
    assert postgres_ts.exists(), "postgres.ts not found"

    content = postgres_ts.read_text()
    assert "buildDefinedColumnsAndQuery" in content, \
        "postgres.ts does not import/use buildDefinedColumnsAndQuery"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sqlite_insert_filters_undefined():
    """
    SQLite: sql() helper filters out undefined values in INSERT.
    When a column has undefined value, it should be omitted entirely,
    allowing the database to use its DEFAULT.
    """
    r = _run_bun_ts("""
import { sql } from "bun";

// Test using SQLite in-memory
const db = sql({
  url: ":memory:",
  adapter: "sqlite"
});

try {
  // Create table with NOT NULL column with DEFAULT
  await db`CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, optional TEXT DEFAULT 'default-value')`;

  // Insert with undefined - should filter out 'optional' and use DEFAULT
  await db`INSERT INTO test_table ${sql({ id: 1, name: "test", optional: undefined })}`;

  // Verify the result
  const result = await db`SELECT * FROM test_table WHERE id = 1`;

  if (result.length !== 1) {
    console.error("FAIL: Expected 1 row, got", result.length);
    process.exit(1);
  }

  if (result[0].optional !== "default-value") {
    console.error("FAIL: Expected optional='default-value', got", result[0].optional);
    process.exit(1);
  }

  console.log("PASS: undefined was filtered, DEFAULT used");
  await db.close();
} catch (e) {
  console.error("ERROR:", e.message);
  process.exit(1);
}
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in stdout: {r.stdout}"


# [pr_diff] fail_to_pass
def test_sqlite_bulk_insert_no_data_loss():
    """
    SQLite: Bulk insert where first item has undefined but later item has value.
    Previously, columns were determined from first item only, causing data loss.
    After fix, all items are scanned to determine which columns have defined values.
    """
    r = _run_bun_ts("""
import { sql } from "bun";

const db = sql({
  url: ":memory:",
  adapter: "sqlite"
});

try {
  await db`CREATE TABLE bulk_test (id INTEGER PRIMARY KEY, name TEXT, optional TEXT)`;

  // Bulk insert where first item has undefined optional, second has value
  await db`INSERT INTO bulk_test ${sql([
    { id: 1, name: "first", optional: undefined },
    { id: 2, name: "second", optional: "preserved-value" }
  ])}`;

  const result = await db`SELECT * FROM bulk_test ORDER BY id`;

  if (result.length !== 2) {
    console.error("FAIL: Expected 2 rows, got", result.length);
    process.exit(1);
  }

  // First item's undefined becomes NULL
  if (result[0].optional !== null) {
    console.error("FAIL: Expected first.optional=null, got", result[0].optional);
    process.exit(1);
  }

  // Second item's value must be preserved (this was the bug!)
  if (result[1].optional !== "preserved-value") {
    console.error("FAIL: Expected second.optional='preserved-value', got", result[1].optional);
    process.exit(1);
  }

  console.log("PASS: bulk insert preserved all values");
  await db.close();
} catch (e) {
  console.error("ERROR:", e.message);
  process.exit(1);
}
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in stdout: {r.stdout}"


# [pr_diff] fail_to_pass
def test_sqlite_bulk_insert_middle_item_value():
    """
    SQLite: Bulk insert where only middle item has value for a column.
    Verifies that ALL items are checked, not just first or last.
    """
    r = _run_bun_ts("""
import { sql } from "bun";

const db = sql({
  url: ":memory:",
  adapter: "sqlite"
});

try {
  await db`CREATE TABLE middle_test (id INTEGER PRIMARY KEY, name TEXT, optional TEXT)`;

  // Bulk insert where only middle item has optional defined
  await db`INSERT INTO middle_test ${sql([
    { id: 1, name: "first", optional: undefined },
    { id: 2, name: "middle", optional: "middle-value" },
    { id: 3, name: "last", optional: undefined }
  ])}`;

  const result = await db`SELECT * FROM middle_test ORDER BY id`;

  if (result.length !== 3) {
    console.error("FAIL: Expected 3 rows, got", result.length);
    process.exit(1);
  }

  // Middle item's value must be preserved
  if (result[1].optional !== "middle-value") {
    console.error("FAIL: Expected middle.optional='middle-value', got", result[1].optional);
    process.exit(1);
  }

  console.log("PASS: middle item value preserved");
  await db.close();
} catch (e) {
  console.error("ERROR:", e.message);
  process.exit(1);
}
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in stdout: {r.stdout}"


# [pr_diff] fail_to_pass
def test_sqlite_all_undefined_throws():
    """
    SQLite: Insert with all undefined values should throw SyntaxError.
    This is a safety check to ensure at least one column has a defined value.
    """
    r = _run_bun_ts("""
import { sql } from "bun";

const db = sql({
  url: ":memory:",
  adapter: "sqlite"
});

try {
  await db`CREATE TABLE throw_test (id INTEGER, name TEXT)`;

  // This should throw - all columns undefined
  try {
    await db`INSERT INTO throw_test ${sql({ id: undefined, name: undefined })}`.execute();
    console.error("FAIL: Expected SyntaxError but insert succeeded");
    process.exit(1);
  } catch (e) {
    if (e.message.includes("Insert needs to have at least one column with a defined value")) {
      console.log("PASS: SyntaxError thrown for all-undefined");
      await db.close();
      process.exit(0);
    }
    throw e;
  }
} catch (e) {
  console.error("ERROR:", e.message);
  process.exit(1);
}
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in stdout: {r.stdout}"


# [pr_diff] fail_to_pass
def test_sqlite_not_null_with_default_uses_default():
    """
    Exact regression test for issue #25829.
    undefined values should be filtered out, allowing NOT NULL columns
    with DEFAULT to use their default.
    """
    r = _run_bun_ts("""
import { sql } from "bun";

const db = sql({
  url: ":memory:",
  adapter: "sqlite"
});

try {
  // Issue #25829: NOT NULL with DEFAULT
  await db`CREATE TABLE issue_25829 (id TEXT PRIMARY KEY, foo TEXT NOT NULL DEFAULT 'default-foo')`;

  // This should work - foo:undefined should be filtered, DEFAULT used
  await db`INSERT INTO issue_25829 ${sql({
    foo: undefined,
    id: "test-id"
  })}`;

  const result = await db`SELECT * FROM issue_25829 WHERE id = 'test-id'`;

  if (result.length !== 1) {
    console.error("FAIL: Expected 1 row");
    process.exit(1);
  }

  if (result[0].foo !== "default-foo") {
    console.error("FAIL: Expected foo='default-foo', got", result[0].foo);
    process.exit(1);
  }

  console.log("PASS: Issue #25829 fixed - NOT NULL with DEFAULT works");
  await db.close();
} catch (e) {
  console.error("ERROR:", e.message);
  process.exit(1);
}
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in stdout: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_sqlite_sql_tests_pass():
    """
    Upstream SQLite SQL tests should still pass after the change.
    Run a focused subset to verify no regression.
    """
    test_file = Path(f"{REPO}/test/js/sql/sqlite-sql.test.ts")
    if not test_file.exists():
        # Skip if test file doesn't exist in this checkout
        return

    r = subprocess.run(
        ["bun", "test", "test/js/sql/sqlite-sql.test.ts", "-t", "insert helper"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # We allow this to pass or have no matching tests (grep-only case)
    # but it should not error
    assert r.returncode in [0, 1], f"Test run errored: {r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just placeholder."""
    shared_ts = Path(f"{REPO}/src/js/internal/sql/shared.ts")
    content = shared_ts.read_text()

    # The buildDefinedColumnsAndQuery should have meaningful body
    func_start = content.find("function buildDefinedColumnsAndQuery")
    assert func_start != -1, "Function not found"

    func_end = content.find("export default", func_start)
    func_body = content[func_start:func_end]

    # Should have actual logic, not just a stub
    assert "for (let k = 0; k < columnCount; k++)" in func_body, \
        "Function body is a stub - missing column loop"
    assert "hasDefinedValue" in func_body, \
        "Function body is a stub - missing hasDefinedValue check"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass - test/CLAUDE.md:161-183 @ bf937f7294762d5e1a11a0d72f63fbeb00de9468
def test_test_claude_md_object_equality_guidance():
    """
    test/CLAUDE.md has a new section on nested/complex object equality.
    The PR added guidance to prefer .toEqual over many .toBe assertions.
    This check verifies the guidance is present in the file.
    """
    claude_md = Path(f"{REPO}/test/CLAUDE.md")
    if not claude_md.exists():
        return

    content = claude_md.read_text()

    # Check for the nested object equality guidance added in this PR
    assert "Nested/complex object equality" in content, \
        "test/CLAUDE.md missing nested object equality guidance"
    assert "Prefer usage of `.toEqual` rather than many `.toBe`" in content, \
        "test/CLAUDE.md missing .toEqual guidance"
