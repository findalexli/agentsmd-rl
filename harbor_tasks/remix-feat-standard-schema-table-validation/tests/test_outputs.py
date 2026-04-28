"""
Task: remix-feat-standard-schema-table-validation
Repo: remix-run/remix @ 89db125c56d3b0d637a283ac9122c6cb8f5542c3
PR:   remix-run/remix#11067

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/remix"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a TypeScript snippet to a temp file and run it with Node.js type stripping."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ts", delete=False, dir=REPO
    ) as f:
        f.write(script)
        tmp = f.name
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", tmp],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_table_standard_schema_partial():
    """Table accepts partial objects via Standard Schema validate (parseSafe)."""
    r = _run_ts(
        """
import { createTable } from '@remix-run/data-table'
import { number, string } from '@remix-run/data-schema'

let users = createTable({
  name: 'users',
  columns: { id: number(), email: string() },
})

let std = users['~standard']
if (!std || typeof std.validate !== 'function') {
  console.error('Missing ~standard')
  process.exit(1)
}

let result = std.validate({ id: 42 })
if (!('value' in result)) {
  console.error('Partial input should succeed, got:', JSON.stringify(result))
  process.exit(1)
}
if (result.value.id !== 42) {
  console.error('Parsed value wrong:', JSON.stringify(result.value))
  process.exit(1)
}
console.log('PASS')
"""
    )
    assert r.returncode == 0, f"Partial parse failed:\n{r.stderr}\n{r.stdout}"


def test_table_standard_schema_unknown_column():
    """Table rejects unknown columns with path info via Standard Schema validate."""
    r = _run_ts(
        """
import { createTable } from '@remix-run/data-table'
import { number, string } from '@remix-run/data-schema'

let users = createTable({
  name: 'users',
  columns: { id: number(), email: string() },
})

let result = users['~standard'].validate({ id: 1, extra: 'x' })
if (!('issues' in result)) {
  console.error('Unknown column should fail, got:', JSON.stringify(result))
  process.exit(1)
}
let first = result.issues[0]
if (!first.message || !first.message.includes('Unknown column')) {
  console.error('Issue message wrong:', first.message)
  process.exit(1)
}
if (!first.path || first.path[0] !== 'extra') {
  console.error('Issue path should be ["extra"], got:', JSON.stringify(first.path))
  process.exit(1)
}
console.log('PASS')
"""
    )
    assert r.returncode == 0, f"Unknown column rejection failed:\n{r.stderr}\n{r.stdout}"


def test_table_standard_schema_invalid_value():
    """Table rejects invalid column values via Standard Schema validate."""
    r = _run_ts(
        """
import { createTable } from '@remix-run/data-table'
import { number, string } from '@remix-run/data-schema'

let users = createTable({
  name: 'users',
  columns: { id: number(), email: string() },
})

let result = users['~standard'].validate({ id: 'not-a-number' })
if (!('issues' in result)) {
  console.error('Invalid value should fail, got:', JSON.stringify(result))
  process.exit(1)
}
let first = result.issues[0]
if (!first.path || first.path[0] !== 'id') {
  console.error('Issue path should be ["id"], got:', JSON.stringify(first.path))
  process.exit(1)
}
console.log('PASS')
"""
    )
    assert r.returncode == 0, f"Invalid value rejection failed:\n{r.stderr}\n{r.stdout}"


def test_table_standard_schema_with_parseSafe():
    """parseSafe from data-schema works directly on table objects."""
    r = _run_ts(
        """
import { createTable } from '@remix-run/data-table'
import { number, string, parseSafe } from '@remix-run/data-schema'

let users = createTable({
  name: 'users',
  columns: { id: number(), email: string() },
})

// Valid partial
let ok = parseSafe(users, { email: 'a@b.com' })
if (!ok.success) {
  console.error('parseSafe on valid partial failed')
  process.exit(1)
}
if (ok.value.email !== 'a@b.com') {
  console.error('Parsed email wrong')
  process.exit(1)
}

// Invalid: unknown column
let bad = parseSafe(users, { id: 1, role: 'admin' })
if (bad.success) {
  console.error('parseSafe should reject unknown column "role"')
  process.exit(1)
}

console.log('PASS')
"""
    )
    assert r.returncode == 0, f"parseSafe test failed:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update checks
# ---------------------------------------------------------------------------


def test_agents_md_cross_package_rule():
    """AGENTS.md must document the cross-package boundaries rule."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "re-export" in content.lower() or "reexport" in content.lower(), (
        "AGENTS.md should mention avoiding re-exports (cross-package boundary rule)"
    )
    assert "cross-package" in content.lower() or "owning package" in content.lower(), (
        "AGENTS.md should document the cross-package boundaries rule about importing from owning package"
    )


def test_readme_documents_data_validation():
    """packages/data-table/README.md must document data validation behavior."""
    readme = Path(REPO) / "packages/data-table/README.md"
    content = readme.read_text()
    # Check for the Data Validation section
    assert "data validation" in content.lower(), (
        "README should have a Data Validation section"
    )
    # Check that Standard Schema compatibility is mentioned
    assert "standard schema" in content.lower() or "standardschema" in content.lower(), (
        "README should mention Standard Schema compatibility"
    )
    # Check that partial objects are documented
    assert "partial" in content.lower(), (
        "README should document that partial objects are allowed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_existing_table_tests_pass():
    """Pre-existing table tests still pass after changes."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/table.test.ts",
        ],
        cwd=f"{REPO}/packages/data-table",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Table tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_table_operators_tests_pass():
    """Table operators tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/operators.test.ts",
        ],
        cwd=f"{REPO}/packages/data-table",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Operators tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_table_inflection_tests_pass():
    """Table inflection tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/inflection.test.ts",
        ],
        cwd=f"{REPO}/packages/data-table",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Inflection tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_database_tests_pass():
    """Database tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/database.test.ts",
        ],
        cwd=f"{REPO}/packages/data-table",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Database tests failed:\n{r.stdout}\n{r.stderr}"


def test_create_table_basic():
    """Basic createTable functionality is not broken."""
    r = _run_ts(
        """
import { createTable, tableMetadataKey } from '@remix-run/data-table'
import { number, string } from '@remix-run/data-schema'

let users = createTable({
  name: 'users',
  columns: { id: number(), email: string() },
  primaryKey: ['id'],
})

let meta = users[tableMetadataKey]
if (meta.name !== 'users') {
  console.error('Table name wrong:', meta.name)
  process.exit(1)
}
if (meta.primaryKey[0] !== 'id') {
  console.error('Primary key wrong:', meta.primaryKey)
  process.exit(1)
}
// Column reference should exist
if (typeof users.id !== 'object' || users.id === null) {
  console.error('Column reference id missing')
  process.exit(1)
}
if (typeof users.email !== 'object' || users.email === null) {
  console.error('Column reference email missing')
  process.exit(1)
}
console.log('PASS')
"""
    )
    assert r.returncode == 0, f"Basic createTable broken:\n{r.stderr}\n{r.stdout}"


def test_not_stub():
    """Table validate has real logic — rejects non-objects and reports multiple issues."""
    r = _run_ts(
        """
import { createTable } from '@remix-run/data-table'
import { number, string } from '@remix-run/data-schema'

let table = createTable({ name: 't', columns: { id: number(), name: string() } })
let std = table['~standard']

// Rejects null
let r1 = std.validate(null)
if (!('issues' in r1)) {
  console.error('should reject null')
  process.exit(1)
}

// Rejects arrays
let r2 = std.validate([1, 2])
if (!('issues' in r2)) {
  console.error('should reject arrays')
  process.exit(1)
}

// Empty object passes (partial allowed)
let r3 = std.validate({})
if (!('value' in r3)) {
  console.error('empty object should pass')
  process.exit(1)
}

// Multiple unknown columns all reported
let r4 = std.validate({ a: 1, b: 2 })
if (!('issues' in r4)) {
  console.error('should reject unknown columns')
  process.exit(1)
}
if (r4.issues.length < 2) {
  console.error('should report all unknown columns, got', r4.issues.length)
  process.exit(1)
}

console.log('PASS')
"""
    )
    assert r.returncode == 0, f"Anti-stub check failed:\n{r.stderr}\n{r.stdout}"


def test_repo_type_safety_tests_pass():
    """Type safety tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/type-safety.test.ts",
        ],
        cwd=f"{REPO}/packages/data-table",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Type safety tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_data_schema_schema_tests_pass():
    """Data-schema schema tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/schema.test.ts",
        ],
        cwd=f"{REPO}/packages/data-schema",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Data-schema schema tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_data_schema_checks_tests_pass():
    """Data-schema checks tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--test",
            "./src/lib/checks.test.ts",
        ],
        cwd=f"{REPO}/packages/data-schema",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Data-schema checks tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_data_schema_parse_tests_pass():
    '''Data-schema parse tests pass (pass_to_pass).'''
    r = subprocess.run(
        [
            'node',
            '--experimental-strip-types',
            '--test',
            './src/lib/parse.test.ts',
        ],
        cwd=f'{REPO}/packages/data-schema',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f'Data-schema parse tests failed:\n{r.stdout}\n{r.stderr}'


def test_repo_data_schema_lazy_tests_pass():
    '''Data-schema lazy tests pass (pass_to_pass).'''
    r = subprocess.run(
        [
            'node',
            '--experimental-strip-types',
            '--test',
            './src/lib/lazy.test.ts',
        ],
        cwd=f'{REPO}/packages/data-schema',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f'Data-schema lazy tests failed:\n{r.stdout}\n{r.stderr}'


def test_repo_data_schema_coerce_tests_pass():
    '''Data-schema coerce tests pass (pass_to_pass).'''
    r = subprocess.run(
        [
            'node',
            '--experimental-strip-types',
            '--test',
            './src/lib/coerce.test.ts',
        ],
        cwd=f'{REPO}/packages/data-schema',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f'Data-schema coerce tests failed:\n{r.stdout}\n{r.stderr}'


def test_repo_data_schema_pipe_tests_pass():
    '''Data-schema pipe tests pass (pass_to_pass).'''
    r = subprocess.run(
        [
            'node',
            '--experimental-strip-types',
            '--test',
            './src/lib/pipe.test.ts',
        ],
        cwd=f'{REPO}/packages/data-schema',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f'Data-schema pipe tests failed:\n{r.stdout}\n{r.stderr}'


def test_repo_data_schema_variant_tests_pass():
    '''Data-schema variant tests pass (pass_to_pass).'''
    r = subprocess.run(
        [
            'node',
            '--experimental-strip-types',
            '--test',
            './src/lib/variant.test.ts',
        ],
        cwd=f'{REPO}/packages/data-schema',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f'Data-schema variant tests failed:\n{r.stdout}\n{r.stderr}'


def test_repo_lint():
    """Repo's linter passes on modified packages (pass_to_pass)."""
    r = subprocess.run(
        ['pnpm', 'lint', 'packages/data-table/src', 'packages/data-schema/src'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_format_check():
    """Repo's format check passes on modified packages (pass_to_pass)."""
    r = subprocess.run(
        ['pnpm', 'format:check', 'packages/data-table', 'packages/data-schema'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


def test_repo_data_table_typecheck():
    """Data-table typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ['pnpm', 'typecheck'],
        cwd=f'{REPO}/packages/data-table',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Data-table typecheck failed:\n{r.stderr[-500:]}"


def test_repo_data_schema_typecheck():
    """Data-schema typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ['pnpm', 'typecheck'],
        cwd=f'{REPO}/packages/data-schema',
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Data-schema typecheck failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_mysql_integration_run_mysql_integration_tests():
    """pass_to_pass | CI job 'MySQL Integration' → step 'Run mysql integration tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/data-table-mysql run test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run mysql integration tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_and_build_run_data_table_package_checks():
    """pass_to_pass | CI job 'Unit and Build' → step 'Run data-table package checks'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/data-table run typecheck && pnpm --filter @remix-run/data-table run test && pnpm --filter @remix-run/data-table run build && pnpm --filter @remix-run/data-table-postgres run typecheck && pnpm --filter @remix-run/data-table-postgres run test && pnpm --filter @remix-run/data-table-postgres run build && pnpm --filter @remix-run/data-table-mysql run typecheck && pnpm --filter @remix-run/data-table-mysql run test && pnpm --filter @remix-run/data-table-mysql run build && pnpm --filter @remix-run/data-table-sqlite run typecheck && pnpm --filter @remix-run/data-table-sqlite run test && pnpm --filter @remix-run/data-table-sqlite run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run data-table package checks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_sqlite_integration_build_sqlite_native_module():
    """pass_to_pass | CI job 'SQLite Integration' → step 'Build sqlite native module'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm rebuild better-sqlite3'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build sqlite native module' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_sqlite_integration_run_sqlite_adapter_tests():
    """pass_to_pass | CI job 'SQLite Integration' → step 'Run sqlite adapter tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/data-table-sqlite run test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run sqlite adapter tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_postgres_integration_run_postgres_integration_tests():
    """pass_to_pass | CI job 'Postgres Integration' → step 'Run postgres integration tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/data-table-postgres run test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run postgres integration tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_is_standard_schema_compatible_with_create_style_():
    """fail_to_pass | PR added test 'is standard-schema compatible with create-style validation semantics' in 'packages/data-table/src/lib/table.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/data-table/src/lib/table.test.ts" -t "is standard-schema compatible with create-style validation semantics" 2>&1 || npx vitest run "packages/data-table/src/lib/table.test.ts" -t "is standard-schema compatible with create-style validation semantics" 2>&1 || pnpm jest "packages/data-table/src/lib/table.test.ts" -t "is standard-schema compatible with create-style validation semantics" 2>&1 || npx jest "packages/data-table/src/lib/table.test.ts" -t "is standard-schema compatible with create-style validation semantics" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'is standard-schema compatible with create-style validation semantics' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
