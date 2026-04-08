"""
Task: remix-featdatatable-add-standardschema-table-validation
Repo: remix-run/remix @ 89db125c56d3b0d637a283ac9122c6cb8f5542c3
PR:   11067

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/remix"

TABLE_TS = f"{REPO}/packages/data-table/src/lib/table.ts"
DATABASE_TS = f"{REPO}/packages/data-table/src/lib/database.ts"
INDEX_TS = f"{REPO}/packages/data-table/src/index.ts"
AGENTS_MD = f"{REPO}/AGENTS.md"
README_MD = f"{REPO}/packages/data-table/README.md"


# ---------------------------------------------------------------------------
# Helpers — install workspace deps and run TypeScript via Node
# ---------------------------------------------------------------------------

_DEPS_INSTALLED = False


def _ensure_deps():
    """Install pnpm workspace deps for data-table (once per session)."""
    global _DEPS_INSTALLED
    if _DEPS_INSTALLED:
        return
    marker = Path(REPO) / "node_modules/.harbor_eval_marker"
    if marker.exists():
        _DEPS_INSTALLED = True
        return
    r = subprocess.run(
        [
            "bash", "-c",
            "corepack enable pnpm 2>/dev/null; "
            "pnpm install --filter @remix-run/data-table... "
            "--ignore-scripts",
        ],
        cwd=REPO, timeout=180,
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr}"
    marker.touch()
    _DEPS_INSTALLED = True


def _run_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a .mts file into the repo root and execute it with Node."""
    _ensure_deps()
    script = Path(REPO) / "_eval_test.mts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — basic file sanity
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified TypeScript files must be valid (no obvious syntax errors)."""
    for path in [TABLE_TS, DATABASE_TS, INDEX_TS]:
        src = Path(path).read_text()
        assert len(src.strip()) > 0, f"{path} is empty"
        assert src.count("{") == src.count("}"), f"{path} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_standard_schema_validation():
    """createTable produces Standard Schema-compatible tables: parseSafe works."""
    r = _run_ts("""
import { createTable } from './packages/data-table/src/lib/table.ts'
import { number, string, parseSafe } from '@remix-run/data-schema'

let users = createTable({
  name: 'eval_users',
  columns: { id: number(), email: string() },
})

// Table must expose ~standard with version, vendor, validate
let std = users['~standard']
if (!std || std.version !== 1 || typeof std.validate !== 'function') {
  console.error('FAIL: table missing ~standard property')
  process.exit(1)
}

// Partial input accepted
let partial = parseSafe(users, { id: 42 })
if (!partial.success) {
  console.error('FAIL: partial input rejected')
  process.exit(1)
}

// Unknown columns rejected
let unknown = parseSafe(users, { id: 1, bogus: 'nope' })
if (unknown.success) {
  console.error('FAIL: unknown column was accepted')
  process.exit(1)
}

// Invalid column value rejected
let invalid = parseSafe(users, { id: 'not-a-number' })
if (invalid.success) {
  console.error('FAIL: invalid value was accepted')
  process.exit(1)
}

console.log('PASS')
""")
    assert r.returncode == 0, f"Standard Schema test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_validate_partial_row_exported():
    """validatePartialRow is exported from table.ts and callable."""
    r = _run_ts("""
import { validatePartialRow, createTable } from './packages/data-table/src/lib/table.ts'
import { number, string } from '@remix-run/data-schema'

if (typeof validatePartialRow !== 'function') {
  console.error('FAIL: validatePartialRow not exported')
  process.exit(1)
}

let users = createTable({
  name: 'eval_users',
  columns: { id: number(), email: string() },
})

let ok = validatePartialRow(users, { id: 1 })
if ('issues' in ok) {
  console.error('FAIL: valid input rejected')
  process.exit(1)
}

let bad = validatePartialRow(users, { id: 1, extra: 'x' })
if (!('issues' in bad)) {
  console.error('FAIL: unknown column accepted')
  process.exit(1)
}

console.log('PASS')
""")
    assert r.returncode == 0, f"validatePartialRow test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural checks
# ---------------------------------------------------------------------------


def test_write_path_uses_shared_validator():
    """database.ts imports validatePartialRow from table.ts for write validation."""
    src = Path(DATABASE_TS).read_text()
    assert re.search(
        r"import.*validatePartialRow.*from\s+['\"]\.\/table", src, re.DOTALL
    ), "database.ts must import validatePartialRow from './table'"
    assert re.search(
        r"validatePartialRow\s*\(", src
    ), "database.ts must call validatePartialRow"


def test_dataschema_type_removed_from_exports():
    """DataSchema type must NOT be re-exported from data-table index.ts."""
    src = Path(INDEX_TS).read_text()
    export_lines = [line for line in src.splitlines() if "export" in line]
    for line in export_lines:
        assert "DataSchema" not in line, (
            "DataSchema must not be re-exported from index.ts"
        )


def test_timestamp_schema_uses_create_schema():
    """timestampSchema uses createSchema from data-schema instead of inline ~standard."""
    src = Path(TABLE_TS).read_text()
    assert re.search(
        r"import.*createSchema.*from\s+['\"]@remix-run/data-schema['\"]",
        src, re.DOTALL,
    ), "table.ts must import createSchema from @remix-run/data-schema"
    match = re.search(
        r"function\s+timestampSchema\s*\([^)]*\)[^{]*\{([\s\S]*?)\n\}", src
    )
    assert match, "timestampSchema function not found"
    assert "createSchema" in match.group(1), (
        "timestampSchema must use createSchema"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/doc update checks
# ---------------------------------------------------------------------------


def test_agents_md_cross_package_rule():
    """AGENTS.md documents cross-package boundary rule about re-exports."""
    content = Path(AGENTS_MD).read_text().lower()
    assert "cross-package" in content, (
        "AGENTS.md must document a cross-package boundary rule"
    )
    has_reexport_rule = (
        ("avoid" in content or "don't" in content or "do not" in content)
        and "re-export" in content
    )
    has_import_directly = "import" in content and "directly" in content
    assert has_reexport_rule or has_import_directly, (
        "AGENTS.md must state that re-exporting from other packages should be avoided"
    )


def test_readme_data_validation():
    """README documents data validation and Standard Schema compatibility."""
    content = Path(README_MD).read_text().lower()
    assert "standard schema" in content, (
        "README must mention Standard Schema compatibility"
    )
    assert "parsesafe" in content or "parse(" in content, (
        "README must show how to use parseSafe/parse with tables"
    )
    assert "partial" in content, (
        "README must explain that partial objects are accepted"
    )
    assert "unknown" in content, (
        "README must explain that unknown columns are rejected"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------


def test_table_still_exports_core_api():
    """Core table API (createTable, hasMany, etc.) must remain exported."""
    src = Path(TABLE_TS).read_text()
    for fn in ["createTable", "hasMany", "hasOne", "belongsTo"]:
        assert re.search(rf"export\s+function\s+{fn}", src), (
            f"{fn} must still be exported"
        )
