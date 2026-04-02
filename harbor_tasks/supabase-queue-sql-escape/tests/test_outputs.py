"""
Task: supabase-queue-sql-escape
Repo: supabase @ 273102323d2959bf5e24678a3388409e91e2ccb4
PR:   44451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"
QUEUE_DIR = f"{REPO}/apps/studio/data/database-queues"

SEND_FILE = f"{QUEUE_DIR}/database-queue-messages-send-mutation.ts"
QUERY_FILE = f"{QUEUE_DIR}/database-queue-messages-infinite-query.ts"
ARCHIVE_FILE = f"{QUEUE_DIR}/database-queue-messages-archive-mutation.ts"
DELETE_FILE = f"{QUEUE_DIR}/database-queue-messages-delete-mutation.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    for fpath in [SEND_FILE, QUERY_FILE, ARCHIVE_FILE, DELETE_FILE]:
        src = Path(fpath).read_text()
        # Basic TS/JS syntax: balanced braces, no stray backtick-only lines
        open_braces = src.count("{")
        close_braces = src.count("}")
        assert abs(open_braces - close_braces) <= 1, (
            f"{Path(fpath).name}: unbalanced braces ({open_braces} open, {close_braces} close)"
        )
        # Verify file still contains the executeSql call (not deleted/emptied)
        assert "executeSql" in src, f"{Path(fpath).name}: missing executeSql call"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_send_payload_escaped():
    """Send mutation must not use raw string interpolation for payload, queueName, or delay."""
    src = Path(SEND_FILE).read_text()

    # The vulnerable pattern: raw '${payload}' or '${queueName}' in SQL
    assert "'${payload}'" not in src, (
        "Send mutation still uses raw '${payload}' interpolation — SQL injection risk"
    )
    assert "'${queueName}'" not in src or "'${queueName}'" not in _extract_sql_context(src), (
        "Send mutation still uses raw '${queueName}' in SQL — SQL injection risk"
    )

    # Verify SQL construction still exists and references pgmq.send
    assert "pgmq.send" in src, "Send mutation missing pgmq.send SQL call"

    # Verify some form of escaping/parameterization is used for payload
    # Accept: literal(payload), literal(queueName), or other escaping patterns
    sql_lines = [l for l in src.splitlines() if "pgmq.send" in l]
    assert len(sql_lines) > 0, "No pgmq.send SQL line found"
    sql_line = sql_lines[0]
    # Must NOT have raw ${payload} in the SQL template
    assert "${payload}" not in sql_line, (
        "pgmq.send SQL line still uses raw ${payload} interpolation"
    )


# [pr_diff] fail_to_pass
def test_query_timestamp_escaped():
    """Infinite query must not use raw string interpolation for afterTimestamp in SQL."""
    src = Path(QUERY_FILE).read_text()

    # The vulnerable pattern: WHERE enqueued_at > '${afterTimestamp}'
    assert "'${afterTimestamp}'" not in src, (
        "Infinite query still uses raw '${afterTimestamp}' — SQL injection risk"
    )

    # Verify WHERE clause still exists with enqueued_at
    assert "enqueued_at" in src, "Query missing enqueued_at filter"

    # The WHERE line must not have raw interpolation
    where_lines = [l for l in src.splitlines() if "enqueued_at" in l and "WHERE" in l]
    for line in where_lines:
        assert "'${" not in line, (
            f"Raw interpolation in WHERE clause: {line.strip()}"
        )


# [pr_diff] fail_to_pass
def test_archive_params_escaped():
    """Archive mutation must not use raw string interpolation for queueName or messageId."""
    src = Path(ARCHIVE_FILE).read_text()

    # Find the pgmq.archive SQL line
    sql_lines = [l for l in src.splitlines() if "pgmq.archive" in l and "sql" in l.lower()]
    assert len(sql_lines) > 0, "No pgmq.archive SQL line found"

    sql_line = sql_lines[0]
    # Must not have raw '${queueName}' pattern
    assert "'${queueName}'" not in sql_line, (
        "Archive mutation uses raw '${queueName}' in SQL"
    )
    # Must not have raw ${messageId} without escaping
    assert _has_no_raw_interpolation(sql_line, "messageId"), (
        "Archive mutation uses raw ${messageId} in SQL without escaping"
    )


# [pr_diff] fail_to_pass
def test_delete_params_escaped():
    """Delete mutation must not use raw string interpolation for queueName or messageId."""
    src = Path(DELETE_FILE).read_text()

    sql_lines = [l for l in src.splitlines() if "pgmq.delete" in l and "sql" in l.lower()]
    assert len(sql_lines) > 0, "No pgmq.delete SQL line found"

    sql_line = sql_lines[0]
    assert "'${queueName}'" not in sql_line, (
        "Delete mutation uses raw '${queueName}' in SQL"
    )
    assert _has_no_raw_interpolation(sql_line, "messageId"), (
        "Delete mutation uses raw ${messageId} in SQL without escaping"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_literal_escapes_quotes():
    """The pg-format literal() function correctly escapes single quotes."""
    # Run the repo's own literal() function with a malicious input
    script = """\
import { literal } from './packages/pg-meta/src/pg-format/index.ts';

// Test single-quote escaping
const result1 = literal("it's a value");
if (!result1.includes("''")) {
    console.error("FAIL: literal() did not double single quotes:", result1);
    process.exit(1);
}
// Must be wrapped in quotes
if (!result1.startsWith("'") || !result1.endsWith("'")) {
    console.error("FAIL: literal() did not wrap in quotes:", result1);
    process.exit(1);
}

// Test SQL injection payload
const result2 = literal("'; DROP TABLE users; --");
if (result2.includes("'; DROP")) {
    console.error("FAIL: literal() did not escape injection:", result2);
    process.exit(1);
}

// Test numeric passthrough
const result3 = literal(42);
if (result3 !== "42") {
    console.error("FAIL: literal(42) should be '42', got:", result3);
    process.exit(1);
}

// Test null handling
const result4 = literal(null);
if (result4 !== "NULL") {
    console.error("FAIL: literal(null) should be 'NULL', got:", result4);
    process.exit(1);
}

console.log("All literal() tests passed");
"""
    r = subprocess.run(
        ["tsx", "-e", script],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"literal() escaping test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_sql_functions_still_present():
    """All four queue SQL functions still exist and have executeSql calls."""
    for fpath, fn_name in [
        (SEND_FILE, "sendDatabaseQueueMessage"),
        (QUERY_FILE, "getDatabaseQueue"),
        (ARCHIVE_FILE, "archiveDatabaseQueueMessage"),
        (DELETE_FILE, "deleteDatabaseQueueMessage"),
    ]:
        src = Path(fpath).read_text()
        assert fn_name in src, f"{Path(fpath).name}: function {fn_name} not found"
        assert "executeSql" in src, f"{Path(fpath).name}: executeSql call not found"
        # Verify it has a sql: property in the executeSql call
        assert re.search(r"sql\s*:", src), (
            f"{Path(fpath).name}: no sql: property in executeSql"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_sql_context(src: str) -> str:
    """Extract lines that are likely inside executeSql SQL template literals."""
    lines = src.splitlines()
    sql_lines = []
    in_sql = False
    for line in lines:
        if "sql:" in line or "sql`" in line:
            in_sql = True
        if in_sql:
            sql_lines.append(line)
        if in_sql and ("`" in line and sql_lines and line != sql_lines[0]):
            in_sql = False
    return "\n".join(sql_lines)


def _has_no_raw_interpolation(sql_line: str, var_name: str) -> bool:
    """Check that a variable is not used with raw ${var} interpolation in SQL.

    Returns True if the variable is either:
    - Not present (removed from this line)
    - Wrapped in a function call like literal(var)
    Returns False if raw ${var} appears without function wrapping.
    """
    # Pattern: ${varName} not preceded by a function call like literal(
    raw_pattern = re.compile(r"(?<!\w\()(\$\{" + re.escape(var_name) + r"\})")
    # Also check the simpler case: ${var} directly in template
    if f"${{{var_name}}}" not in sql_line:
        return True  # variable not in this line at all, OK
    # If it's there, it must be inside a function call
    # e.g., ${literal(messageId)} is fine, ${messageId} is not
    # Check if the ${...} contains a function call wrapping the variable
    wrapped = re.search(r"\$\{[a-zA-Z_]+\(" + re.escape(var_name) + r"\)\}", sql_line)
    return wrapped is not None
