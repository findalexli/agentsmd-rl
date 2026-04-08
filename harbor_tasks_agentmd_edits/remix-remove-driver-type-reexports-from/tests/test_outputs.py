"""
Task: remix-remove-driver-type-reexports-from
Repo: remix-run/remix @ 1c0176eae3dd77d18e293c53d54237357ffc8efd
PR:   11160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — driver type re-exports removed
# ---------------------------------------------------------------------------

def test_mysql_exports_only_adapter_types():
    """MySQL index.ts exports only adapter-owned types, not driver-shaped types."""
    r = _run_node(r"""
import fs from 'fs';
const src = fs.readFileSync('packages/data-table-mysql/src/index.ts', 'utf8');
const driverTypes = [
  'MysqlDatabasePool', 'MysqlDatabaseConnection',
  'MysqlQueryResponse', 'MysqlQueryResultHeader', 'MysqlQueryRows',
];
const found = driverTypes.filter(t => new RegExp('\\b' + t + '\\b').test(src));
if (found.length > 0) {
  console.error('FAIL: Driver types still exported: ' + found.join(', '));
  process.exit(1);
}
if (!src.includes('MysqlDatabaseAdapterOptions')) {
  console.error('FAIL: MysqlDatabaseAdapterOptions must remain exported');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_postgres_exports_only_adapter_types():
    """Postgres index.ts exports only adapter-owned types, not driver-shaped types."""
    r = _run_node(r"""
import fs from 'fs';
const src = fs.readFileSync('packages/data-table-postgres/src/index.ts', 'utf8');
const driverTypes = [
  'PostgresDatabasePool', 'PostgresDatabaseClient',
  'PostgresQueryResult', 'PostgresTransactionClient',
];
const found = driverTypes.filter(t => new RegExp('\\b' + t + '\\b').test(src));
if (found.length > 0) {
  console.error('FAIL: Driver types still exported: ' + found.join(', '));
  process.exit(1);
}
if (!src.includes('PostgresDatabaseAdapterOptions')) {
  console.error('FAIL: PostgresDatabaseAdapterOptions must remain exported');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_sqlite_exports_only_adapter_types():
    """SQLite index.ts must not export SqliteDatabaseConnection."""
    r = _run_node(r"""
import fs from 'fs';
const src = fs.readFileSync('packages/data-table-sqlite/src/index.ts', 'utf8');
if (/\bSqliteDatabaseConnection\b/.test(src)) {
  console.error('FAIL: SqliteDatabaseConnection still exported');
  process.exit(1);
}
if (!src.includes('SqliteDatabaseAdapterOptions')) {
  console.error('FAIL: SqliteDatabaseAdapterOptions must remain exported');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — type guard functions added and correct
# ---------------------------------------------------------------------------

def test_mysql_pool_connection_type_guard():
    """isMysqlPoolConnection type guard exists and correctly distinguishes pool connections."""
    r = _run_node(r"""
import fs from 'fs';
const src = fs.readFileSync('packages/data-table-mysql/src/lib/adapter.ts', 'utf8');

// Extract the return expression from isMysqlPoolConnection
const match = src.match(/function\s+isMysqlPoolConnection[\s\S]*?return\s+(.+)/);
if (!match) {
  console.error('FAIL: isMysqlPoolConnection function not found');
  process.exit(1);
}

let expr = match[1].trim().replace(/;?\s*$/, '');
const fn = new Function('connection', 'return ' + expr);

// Pool connection has release method -> true
if (!fn({ release: () => {}, query: () => {} })) {
  console.error('FAIL: Should return true for pool connection with release');
  process.exit(1);
}

// Plain connection without release -> false
if (fn({ query: () => {} })) {
  console.error('FAIL: Should return false for plain connection');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_postgres_pool_type_guard():
    """isPostgresPool type guard exists and correctly identifies pool vs client."""
    r = _run_node(r"""
import fs from 'fs';
const src = fs.readFileSync('packages/data-table-postgres/src/lib/adapter.ts', 'utf8');

// Extract the return expression from isPostgresPool
const match = src.match(/function\s+isPostgresPool[\s\S]*?return\s+(.+)/);
if (!match) {
  console.error('FAIL: isPostgresPool function not found');
  process.exit(1);
}

let expr = match[1].trim().replace(/;?\s*$/, '');
const fn = new Function('client', 'return ' + expr);

// Pool has connect method -> true
if (!fn({ query: () => {}, connect: () => {} })) {
  console.error('FAIL: Should return true for pool with connect');
  process.exit(1);
}

// Plain client without connect -> false
if (fn({ query: () => {} })) {
  console.error('FAIL: Should return false for client without connect');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — adapter uses driver package types directly
# ---------------------------------------------------------------------------

def test_mysql_adapter_imports_driver_package():
    """MySQL adapter imports types directly from mysql2/promise instead of defining custom types."""
    r = _run_node(r"""
import fs from 'fs';
const src = fs.readFileSync('packages/data-table-mysql/src/lib/adapter.ts', 'utf8');

// Must import from the driver package
if (!src.includes("from 'mysql2/promise'") && !src.includes('from "mysql2/promise"')) {
  console.error('FAIL: Adapter does not import from mysql2/promise');
  process.exit(1);
}

// Old custom exported type definitions should be gone
if (/export\s+type\s+MysqlDatabasePool\b/.test(src)) {
  console.error('FAIL: MysqlDatabasePool type still exported');
  process.exit(1);
}
if (/export\s+type\s+MysqlDatabaseConnection\b/.test(src)) {
  console.error('FAIL: MysqlDatabaseConnection type still exported');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — READMEs updated with import instructions
# ---------------------------------------------------------------------------

def test_readmes_redirect_to_driver_packages():
    """READMEs instruct users to import driver-specific types from the original packages."""
    r = _run_node(r"""
import fs from 'fs';
const checks = [
  { file: 'packages/data-table-mysql/README.md', pkg: 'mysql2/promise' },
  { file: 'packages/data-table-postgres/README.md', pkg: 'pg' },
  { file: 'packages/data-table-sqlite/README.md', pkg: 'better-sqlite3' },
];
let failures = [];
for (const { file, pkg } of checks) {
  const src = fs.readFileSync(file, 'utf8');
  const lines = src.split('\n');
  const hasInstruction = lines.some(l =>
    /import/i.test(l) && /directly/i.test(l) && l.includes(pkg)
  );
  if (!hasInstruction) {
    failures.push(file + ': missing instruction to import types from ' + pkg);
  }
}
if (failures.length > 0) {
  console.error('FAIL: ' + failures.join('; '));
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# pass_to_pass (static) — basic validity and exports preserved
# ---------------------------------------------------------------------------

def test_syntax_check():
    """All modified TypeScript source files are non-empty with balanced braces."""
    ts_files = [
        f"{REPO}/packages/data-table-mysql/src/index.ts",
        f"{REPO}/packages/data-table-mysql/src/lib/adapter.ts",
        f"{REPO}/packages/data-table-postgres/src/index.ts",
        f"{REPO}/packages/data-table-postgres/src/lib/adapter.ts",
        f"{REPO}/packages/data-table-sqlite/src/index.ts",
        f"{REPO}/packages/data-table-sqlite/src/lib/adapter.ts",
    ]
    for path in ts_files:
        src = Path(path).read_text()
        assert len(src.strip()) > 0, f"{path} is empty"
        assert src.count("{") == src.count("}"), f"{path} has unbalanced braces"


def test_adapter_classes_still_exported():
    """All adapter classes and factory functions remain exported from index.ts."""
    mysql_src = Path(f"{REPO}/packages/data-table-mysql/src/index.ts").read_text()
    assert "createMysqlDatabaseAdapter" in mysql_src
    assert "MysqlDatabaseAdapter" in mysql_src

    pg_src = Path(f"{REPO}/packages/data-table-postgres/src/index.ts").read_text()
    assert "createPostgresDatabaseAdapter" in pg_src
    assert "PostgresDatabaseAdapter" in pg_src

    sqlite_src = Path(f"{REPO}/packages/data-table-sqlite/src/index.ts").read_text()
    assert "createSqliteDatabaseAdapter" in sqlite_src
    assert "SqliteDatabaseAdapter" in sqlite_src
