"""
Task: supabase-queue-sql-escape
Repo: supabase @ 273102323d2959bf5e24678a3388409e91e2ccb4
PR:   44451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"
QUEUE_DIR = f"{REPO}/apps/studio/data/database-queues"

SEND_FILE = f"{QUEUE_DIR}/database-queue-messages-send-mutation.ts"
QUERY_FILE = f"{QUEUE_DIR}/database-queue-messages-infinite-query.ts"
ARCHIVE_FILE = f"{QUEUE_DIR}/database-queue-messages-archive-mutation.ts"
DELETE_FILE = f"{QUEUE_DIR}/database-queue-messages-delete-mutation.ts"

ALL_FILES = [SEND_FILE, QUERY_FILE, ARCHIVE_FILE, DELETE_FILE]

MOCKS_DIR = f"{REPO}/_test_mocks"

MOCK_EXECUTESQL = '''\
export async function executeSql(args: any) {
  (globalThis as any).__capturedSql = args.sql;
  return { result: [] };
}
'''

MOCK_DEPS = '''\
export function isQueueNameValid() { return true; }
export const QUEUE_MESSAGE_TYPE = {};
export const databaseQueuesKeys = { create: () => [], getMessagesInfinite: () => [] };
export function last(arr: any[]) { return arr?.[arr.length-1]; }
export const DATE_FORMAT = "YYYY-MM-DD";
function dayjs() { return { format: () => "2024-01-01" }; }
dayjs.default = dayjs;
export default dayjs;
'''


def _setup_mocks():
    """Create mock modules and symlinks for behavioral testing."""
    mocks = Path(MOCKS_DIR)
    mocks.mkdir(exist_ok=True)
    (mocks / "execute-sql.ts").write_text(MOCK_EXECUTESQL)
    (mocks / "deps.ts").write_text(MOCK_DEPS)
    nm = Path(REPO) / "node_modules" / "@supabase"
    nm.mkdir(parents=True, exist_ok=True)
    link = nm / "pg-meta"
    if not link.exists():
        link.symlink_to(Path(REPO) / "packages" / "pg-meta")


def _rewrite_imports(src: str, target_dir: str) -> str:
    """Replace real imports with mock imports for isolated execution."""
    mocks_rel = os.path.relpath(MOCKS_DIR, target_dir)

    src = re.sub(
        r"import\s*\{[^}]*\}\s*from\s*['\"]data/sql/execute-sql-query['\"]",
        f'import {{ executeSql }} from "{mocks_rel}/execute-sql.ts"', src)
    src = re.sub(
        r"import\s*\{[^}]*\}\s*from\s*['\"]components/interfaces/Integrations/Queues/Queues\.utils['\"]",
        f'import {{ isQueueNameValid }} from "{mocks_rel}/deps.ts"', src)
    src = re.sub(
        r"import\s*\{[^}]*\}\s*from\s*['\"]components/interfaces/Integrations/Queues/SingleQueue/Queue\.utils['\"]",
        f'import {{ QUEUE_MESSAGE_TYPE }} from "{mocks_rel}/deps.ts"', src)
    src = re.sub(
        r"import\s*\{[^}]*\}\s*from\s*['\"]\.\/keys['\"]",
        f'import {{ databaseQueuesKeys }} from "{mocks_rel}/deps.ts"', src)
    src = re.sub(
        r"import\s+dayjs\s+from\s*['\"]dayjs['\"]",
        f'import dayjs from "{mocks_rel}/deps.ts"', src)
    src = re.sub(
        r"import\s*\{[^}]*\}\s*from\s*['\"]lodash['\"]",
        f'import {{ last }} from "{mocks_rel}/deps.ts"', src)
    src = re.sub(
        r"import\s*\{[^}]*\}\s*from\s*['\"]lib/constants['\"]",
        f'import {{ DATE_FORMAT }} from "{mocks_rel}/deps.ts"', src)
    src = re.sub(r"import\s*\{[^}]*\}\s*from\s*['\"]sonner['\"]", "// removed", src)
    src = re.sub(r"import\s*\{[^}]*\}\s*from\s*['\"]@tanstack/react-query['\"]", "// removed", src)
    src = re.sub(r"import\s+type\s*\{[^}]*\}\s*from\s*['\"]types['\"]", "// removed", src)
    src = re.sub(r"import\s+type\s*\{[^}]*\}\s*from\s*['\"]@tanstack/react-query['\"]", "// removed", src)
    return src


def _make_testable_module(src_file: str, tag: str) -> str:
    """Create a testable copy of a source file with mocked imports."""
    src_dir = str(Path(src_file).parent)
    src = Path(src_file).read_text()
    src = _rewrite_imports(src, src_dir)
    # Remove React hook wrappers that depend on @tanstack/react-query
    src = re.sub(r"export const use\w+(?:Mutation|Query)\b.*", "", src, flags=re.DOTALL)
    tmp_path = Path(src_dir) / f"_eval_{tag}.ts"
    tmp_path.write_text(src)
    return str(tmp_path)


def _run_tsx(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via tsx in the repo directory."""
    script = Path(REPO) / "_eval_caller.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["tsx", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _run_function_capture_sql(src_file: str, tag: str, fn_name: str,
                               call_args: str) -> str:
    """Create a testable module, call the function, and return the captured SQL."""
    _setup_mocks()
    mod_path = _make_testable_module(src_file, tag)
    rel_path = "./" + str(Path(mod_path).relative_to(REPO))

    caller = f'''
import {{ {fn_name} }} from "{rel_path}"

async function main() {{
  try {{
    await {fn_name}({call_args});
    console.log(JSON.stringify({{ sql: (globalThis as any).__capturedSql }}));
  }} catch (e: any) {{
    console.log(JSON.stringify({{ error: e.message }}));
  }}
}}
main();
'''
    r = _run_tsx(caller)
    Path(mod_path).unlink(missing_ok=True)

    assert r.returncode == 0, f"tsx failed for {fn_name}: {r.stderr[:500]}"

    for line in r.stdout.strip().splitlines():
        line = line.strip()
        if line.startswith("{"):
            data = json.loads(line)
            if "sql" in data:
                return data["sql"]
            if "error" in data:
                raise RuntimeError(f"{fn_name} threw: {data['error']}")
    raise RuntimeError(f"No SQL captured from {fn_name}. stdout: {r.stdout[:500]}")


def _assert_value_escaped_in_sql(sql: str, raw_value: str, label: str):
    """Assert that a raw value containing single quotes is properly escaped in the SQL.

    When properly escaped, internal single quotes are doubled. For example,
    "evil'queue" becomes "evil''queue" in the SQL string. We check that the
    doubled-quote form appears in the SQL output. This assertion requires the
    raw_value to contain at least one single quote in a non-leading position.
    """
    escaped = raw_value.replace("'", "''")
    assert escaped in sql, (
        f"{label}: value not properly escaped in SQL. "
        f"Expected escaped form '{escaped}' in SQL. Got: {sql}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
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
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------


def test_literal_escapes_sql_injection():
    """The escaping mechanism must properly handle SQL injection payloads.

    Tests the literal() escaping function directly with various types,
    then calls the actual send function to verify its SQL output is safe.
    """
    # --- Behavioral: run the actual literal() escaping function ---
    r = _run_tsx("""
import { literal } from './packages/pg-meta/src/pg-format/index.ts'

const r1 = literal("it's a value")
console.log(JSON.stringify({name: "single_quote", out: r1}))

const r2 = literal("'; DROP TABLE users; --")
console.log(JSON.stringify({name: "drop_table", out: r2}))

const r3 = literal({key: "it's dangerous"})
console.log(JSON.stringify({name: "object", out: r3}))

const r4 = literal(null)
console.log(JSON.stringify({name: "null", out: r4}))

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

    # --- Behavioral: call the send function with injection and verify SQL ---
    sql = _run_function_capture_sql(
        SEND_FILE, "send_inject", "sendDatabaseQueueMessage",
        '{ projectRef: "p", connectionString: "c", '
        "queueName: \"O'Reilly\", "
        'payload: \'{"key": "value"}\', delay: 5 }'
    )
    # O'Reilly should appear as O''Reilly in the escaped SQL
    _assert_value_escaped_in_sql(sql, "O'Reilly", "send queueName")


def test_send_payload_escaped():
    """Send mutation must produce safe SQL for all user-controlled parameters.

    Calls sendDatabaseQueueMessage with injection payloads for queueName
    and payload, then verifies the generated SQL properly escapes them.
    """
    sql = _run_function_capture_sql(
        SEND_FILE, "send_esc", "sendDatabaseQueueMessage",
        '{ projectRef: "p", connectionString: "c", '
        "queueName: \"evil'queue\", "
        "payload: '{\"msg\": \"it\\'s bad\"}', delay: 5 }"
    )
    # queueName with quote must be escaped
    _assert_value_escaped_in_sql(sql, "evil'queue", "send queueName")
    assert "pgmq.send" in sql, f"Missing pgmq.send call in SQL: {sql}"
    assert "5" in sql, f"Delay value missing from SQL: {sql}"


def test_query_timestamp_escaped():
    """Infinite query must produce safe SQL for the afterTimestamp parameter.

    Calls getDatabaseQueue with a malicious afterTimestamp and verifies
    the generated SQL properly escapes it.
    """
    sql = _run_function_capture_sql(
        QUERY_FILE, "query_esc", "getDatabaseQueue",
        '{ projectRef: "p", connectionString: "c", '
        'queueName: "testqueue", '
        "afterTimestamp: \"2024-01-01'; DROP TABLE users; --\", "
        'status: ["available"] }'
    )
    # Timestamp with injection must be escaped (quote doubled)
    _assert_value_escaped_in_sql(
        sql, "2024-01-01'; DROP TABLE users; --", "query timestamp"
    )
    assert "enqueued_at" in sql, f"Missing enqueued_at in query SQL: {sql}"


def test_archive_params_escaped():
    """Archive mutation must produce safe SQL for queueName and messageId.

    Calls archiveDatabaseQueueMessage with injection payloads and verifies
    the generated SQL properly escapes them.
    """
    sql = _run_function_capture_sql(
        ARCHIVE_FILE, "archive_esc", "archiveDatabaseQueueMessage",
        '{ projectRef: "p", connectionString: "c", '
        "queueName: \"evil'queue\", messageId: 42 }"
    )
    _assert_value_escaped_in_sql(sql, "evil'queue", "archive queueName")
    assert "pgmq.archive" in sql, f"Missing pgmq.archive in SQL: {sql}"
    assert "42" in sql, f"messageId missing from archive SQL: {sql}"


def test_delete_params_escaped():
    """Delete mutation must produce safe SQL for queueName and messageId.

    Calls deleteDatabaseQueueMessage with injection payloads and verifies
    the generated SQL properly escapes them.
    """
    sql = _run_function_capture_sql(
        DELETE_FILE, "delete_esc", "deleteDatabaseQueueMessage",
        '{ projectRef: "p", connectionString: "c", '
        "queueName: \"evil'queue\", messageId: 99 }"
    )
    _assert_value_escaped_in_sql(sql, "evil'queue", "delete queueName")
    assert "pgmq.delete" in sql, f"Missing pgmq.delete in SQL: {sql}"
    assert "99" in sql, f"messageId missing from delete SQL: {sql}"


# ---------------------------------------------------------------------------
# agent_config (pass_to_pass)
# ---------------------------------------------------------------------------


def test_no_as_any_casts():
    """Modified TypeScript files must not use 'as any' type casts."""
    for fpath in ALL_FILES:
        src = Path(fpath).read_text()
        assert " as any" not in src, (
            f"{Path(fpath).name}: contains forbidden 'as any' type cast"
        )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------


def _ensure_deps():
    """Install pnpm and dependencies if not already present."""
    if not Path(f"{REPO}/node_modules/.bin").exists():
        subprocess.run(
            ["npm", "install", "-g", "pnpm@10.24.0"],
            capture_output=True, timeout=120
        )
        env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            capture_output=True, cwd=REPO, timeout=300, env=env
        )


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    _ensure_deps()
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    r = subprocess.run(
        ["pnpm", "run", "typecheck"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/apps/studio",
        env=env
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's lint checks pass (pass_to_pass)."""
    _ensure_deps()
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    r = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/apps/studio",
        env=env
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
