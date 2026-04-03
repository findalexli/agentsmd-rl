"""
Task: supabase-queue-sql-escape
Repo: supabase @ 273102323d2959bf5e24678a3388409e91e2ccb4
PR:   44451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/supabase"
QUEUE_DIR = f"{REPO}/apps/studio/data/database-queues"

SEND_FILE = f"{QUEUE_DIR}/database-queue-messages-send-mutation.ts"
QUERY_FILE = f"{QUEUE_DIR}/database-queue-messages-infinite-query.ts"
ARCHIVE_FILE = f"{QUEUE_DIR}/database-queue-messages-archive-mutation.ts"
DELETE_FILE = f"{QUEUE_DIR}/database-queue-messages-delete-mutation.ts"

ALL_FILES = [SEND_FILE, QUERY_FILE, ARCHIVE_FILE, DELETE_FILE]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    # AST-only because: TS monorepo requires pnpm install + full toolchain to compile
    for fpath in ALL_FILES:
        src = Path(fpath).read_text()
        open_braces = src.count("{")
        close_braces = src.count("}")
        assert abs(open_braces - close_braces) <= 1, (
            f"{Path(fpath).name}: unbalanced braces ({open_braces} open, {close_braces} close)"
        )
        assert "executeSql" in src, f"{Path(fpath).name}: missing executeSql call"


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
        assert re.search(r"sql\s*:", src), (
            f"{Path(fpath).name}: no sql: property in executeSql"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_send_payload_escaped():
    """Send mutation must not use raw string interpolation for payload, queueName, or delay in SQL."""
    # AST-only because: TS monorepo; executeSql requires full React/Next.js context
    src = Path(SEND_FILE).read_text()

    # The vulnerable patterns: raw '${var}' in SQL template
    assert "'${payload}'" not in src, (
        "Send mutation uses raw '${payload}' interpolation — SQL injection risk"
    )
    assert "'${queueName}'" not in src, (
        "Send mutation uses raw '${queueName}' interpolation — SQL injection risk"
    )

    # Verify pgmq.send SQL still exists
    assert "pgmq.send" in src, "Send mutation missing pgmq.send SQL call"

    # The pgmq.send line must not have raw ${payload} or ${delay}
    send_lines = [l for l in src.splitlines() if "pgmq.send" in l]
    assert len(send_lines) > 0, "No pgmq.send line found"
    for line in send_lines:
        assert "'${payload}'" not in line, "pgmq.send uses raw '${payload}'"
        assert "'${queueName}'" not in line, "pgmq.send uses raw '${queueName}'"
        # delay: on base it's ${delay} (no quotes, but still raw interpolation)
        if "${delay}" in line:
            assert re.search(r"\$\{\w+\(delay\)\}", line), (
                "pgmq.send uses raw ${delay} without escaping function"
            )


# [pr_diff] fail_to_pass
def test_query_timestamp_escaped():
    """Infinite query must not use raw string interpolation for afterTimestamp in SQL."""
    # AST-only because: TS monorepo; executeSql requires full React/Next.js context
    src = Path(QUERY_FILE).read_text()

    # The vulnerable pattern: WHERE enqueued_at > '${afterTimestamp}'
    assert "'${afterTimestamp}'" not in src, (
        "Infinite query uses raw '${afterTimestamp}' — SQL injection risk"
    )

    # Verify WHERE clause still references enqueued_at
    assert "enqueued_at" in src, "Query missing enqueued_at filter"

    # The specific afterTimestamp WHERE line must not have raw interpolation
    for line in src.splitlines():
        if "afterTimestamp" in line:
            assert "'${afterTimestamp}'" not in line, (
                f"Raw afterTimestamp interpolation: {line.strip()}"
            )


# [pr_diff] fail_to_pass
def test_archive_params_escaped():
    """Archive mutation must not use raw string interpolation for queueName or messageId."""
    # AST-only because: TS monorepo; executeSql requires full React/Next.js context
    src = Path(ARCHIVE_FILE).read_text()

    # Check for raw '${queueName}' in the file
    assert "'${queueName}'" not in src, (
        "Archive mutation uses raw '${queueName}' in SQL"
    )

    # Check pgmq.archive line — messageId must be wrapped in escaping function
    archive_lines = [l for l in src.splitlines() if "pgmq.archive" in l]
    assert len(archive_lines) > 0, "No pgmq.archive line found"
    for line in archive_lines:
        assert "'${queueName}'" not in line, "Archive uses raw '${queueName}'"
        if "${messageId}" in line:
            assert re.search(r"\$\{\w+\(messageId\)\}", line), (
                "Archive uses raw ${messageId} without escaping function"
            )


# [pr_diff] fail_to_pass
def test_delete_params_escaped():
    """Delete mutation must not use raw string interpolation for queueName or messageId."""
    # AST-only because: TS monorepo; executeSql requires full React/Next.js context
    src = Path(DELETE_FILE).read_text()

    # Check for raw '${queueName}' in the file
    assert "'${queueName}'" not in src, (
        "Delete mutation uses raw '${queueName}' in SQL"
    )

    # Check pgmq.delete line — messageId must be wrapped in escaping function
    delete_lines = [l for l in src.splitlines() if "pgmq.delete" in l]
    assert len(delete_lines) > 0, "No pgmq.delete line found"
    for line in delete_lines:
        assert "'${queueName}'" not in line, "Delete uses raw '${queueName}'"
        if "${messageId}" in line:
            assert re.search(r"\$\{\w+\(messageId\)\}", line), (
                "Delete uses raw ${messageId} without escaping function"
            )


# [agent_config] pass_to_pass — .claude/skills/studio-best-practices/SKILL.md:36 @ 273102323d2959bf5e24678a3388409e91e2ccb4
def test_no_as_any_casts():
    """Modified TypeScript files must not use 'as any' type casts."""
    for fpath in ALL_FILES:
        src = Path(fpath).read_text()
        assert " as any" not in src, (
            f"{Path(fpath).name}: contains forbidden 'as any' type cast"
        )
