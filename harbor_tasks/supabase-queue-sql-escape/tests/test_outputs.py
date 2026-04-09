"""
Task: supabase-queue-sql-escape
Repo: supabase @ 273102323d2959bf5e24678a3388409e91e2ccb4
PR:   44451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"
QUEUE_DIR = f"{REPO}/apps/studio/data/database-queues"

SEND_FILE = f"{QUEUE_DIR}/database-queue-messages-send-mutation.ts"
QUERY_FILE = f"{QUEUE_DIR}/database-queue-messages-infinite-query.ts"
ARCHIVE_FILE = f"{QUEUE_DIR}/database-queue-messages-archive-mutation.ts"
DELETE_FILE = f"{QUEUE_DIR}/database-queue-messages-delete-mutation.ts"

ALL_FILES = [SEND_FILE, QUERY_FILE, ARCHIVE_FILE, DELETE_FILE]


def _run_tsx(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via tsx in the repo directory."""
    script = Path(REPO) / "_eval_tmp.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["tsx", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax and structure checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    for fpath in ALL_FILES:
        src = Path(fpath).read_text()
        open_b = src.count("{")
        close_b = src.count("}")
        assert abs(open_b - close_b) <= 1, (
            f"{Path(fpath).name}: unbalanced braces ({open_b} open, {close_b} close)"
        )
        assert "executeSql" in src, f"{Path(fpath).name}: missing executeSql call"


def test_sql_functions_still_present():
    """All four queue SQL functions still exist with executeSql calls."""
    for fpath, fn_name in [
        (SEND_FILE, "sendDatabaseQueueMessage"),
        (QUERY_FILE, "getDatabaseQueue"),
        (ARCHIVE_FILE, "archiveDatabaseQueueMessage"),
        (DELETE_FILE, "deleteDatabaseQueueMessage"),
    ]:
        src = Path(fpath).read_text()
        assert fn_name in src, f"{Path(fpath).name}: function {fn_name} not found"
        assert "executeSql" in src, f"{Path(fpath).name}: executeSql call not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral + structural tests
# ---------------------------------------------------------------------------


def test_literal_escapes_sql_injection():
    """literal() must correctly escape single quotes and all four files must import it."""
    # --- Behavioral: run the actual literal() function with SQL injection payloads ---
    r = _run_tsx("""
import { literal } from './packages/pg-meta/src/pg-format/index.ts'

// Single quotes must be doubled
const r1 = literal("it's a value")
console.log(JSON.stringify({name: "single_quote", out: r1}))

// Classic SQL injection payload
const r2 = literal("'; DROP TABLE users; --")
console.log(JSON.stringify({name: "drop_table", out: r2}))

// Object with special chars gets jsonb cast
const r3 = literal({key: "it's dangerous"})
console.log(JSON.stringify({name: "object", out: r3}))

// null returns NULL (unquoted)
const r4 = literal(null)
console.log(JSON.stringify({name: "null", out: r4}))

// number returns plain numeric string (no quotes)
const r5 = literal(42)
console.log(JSON.stringify({name: "number", out: r5}))
""")
    assert r.returncode == 0, f"tsx execution failed: {r.stderr}"

    results = {}
    for line in r.stdout.strip().splitlines():
        if line.startswith("{"):
            data = json.loads(line)
            results[data["name"]] = data["out"]

    assert results["single_quote"] == "'it''s a value'", f"Got: {results['single_quote']}"
    assert results["drop_table"] == "'''; DROP TABLE users; --'", f"Got: {results['drop_table']}"
    assert "::jsonb" in results["object"], f"Object missing jsonb cast: {results['object']}"
    assert results["null"] == "NULL", f"Got: {results['null']}"
    assert results["number"] == "42", f"Got: {results['number']}"

    # --- Structural: all four files must import literal (fails on base commit) ---
    for fpath in ALL_FILES:
        src = Path(fpath).read_text()
        assert "import { literal }" in src, (
            f"{Path(fpath).name}: literal not imported — SQL injection not fixed"
        )


def test_send_payload_escaped():
    """Send mutation must use literal() for queueName, payload, and delay in SQL."""
    src = Path(SEND_FILE).read_text()

    # No raw string interpolation in SQL
    assert "'${queueName}'" not in src, "Send mutation still has raw '${queueName}'"
    assert "'${payload}'" not in src, "Send mutation still has raw '${payload}'"

    # pgmq.send line must use literal() for all user-controlled params
    send_lines = [l for l in src.splitlines() if "pgmq.send" in l]
    assert len(send_lines) > 0, "No pgmq.send line found"
    for line in send_lines:
        assert "literal(queueName)" in line, (
            f"pgmq.send missing literal(queueName): {line.strip()}"
        )
        assert "literal(payload)" in line, (
            f"pgmq.send missing literal(payload): {line.strip()}"
        )
        assert "literal(delay)" in line, (
            f"pgmq.send missing literal(delay): {line.strip()}"
        )


def test_query_timestamp_escaped():
    """Infinite query must use literal() for afterTimestamp in WHERE clause."""
    src = Path(QUERY_FILE).read_text()

    assert "'${afterTimestamp}'" not in src, "Query still has raw '${afterTimestamp}'"
    assert "enqueued_at" in src, "Query missing enqueued_at filter"

    # The WHERE clause must use literal(afterTimestamp)
    for line in src.splitlines():
        if "afterTimestamp" in line and "enqueued_at" in line:
            assert "literal(afterTimestamp)" in line, (
                f"WHERE clause missing literal(afterTimestamp): {line.strip()}"
            )


def test_archive_params_escaped():
    """Archive mutation must use literal() for queueName and messageId in SQL."""
    src = Path(ARCHIVE_FILE).read_text()

    assert "'${queueName}'" not in src, "Archive still has raw '${queueName}'"

    archive_lines = [l for l in src.splitlines() if "pgmq.archive" in l]
    assert len(archive_lines) > 0, "No pgmq.archive line found"
    for line in archive_lines:
        assert "literal(queueName)" in line, f"Missing literal(queueName): {line.strip()}"
        assert "literal(messageId)" in line, f"Missing literal(messageId): {line.strip()}"


def test_delete_params_escaped():
    """Delete mutation must use literal() for queueName and messageId in SQL."""
    src = Path(DELETE_FILE).read_text()

    assert "'${queueName}'" not in src, "Delete still has raw '${queueName}'"

    delete_lines = [l for l in src.splitlines() if "pgmq.delete" in l]
    assert len(delete_lines) > 0, "No pgmq.delete line found"
    for line in delete_lines:
        assert "literal(queueName)" in line, f"Missing literal(queueName): {line.strip()}"
        assert "literal(messageId)" in line, f"Missing literal(messageId): {line.strip()}"


# ---------------------------------------------------------------------------
# agent_config (pass_to_pass)
# ---------------------------------------------------------------------------


# .claude/skills/studio-best-practices/SKILL.md:36 @ 273102323d2959bf5e24678a3388409e91e2ccb4
def test_no_as_any_casts():
    """Modified TypeScript files must not use 'as any' type casts."""
    for fpath in ALL_FILES:
        src = Path(fpath).read_text()
        assert " as any" not in src, (
            f"{Path(fpath).name}: contains forbidden 'as any' type cast"
        )
