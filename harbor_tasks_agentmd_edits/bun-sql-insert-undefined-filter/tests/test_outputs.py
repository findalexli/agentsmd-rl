"""
Task: bun-sql-insert-undefined-filter
Repo: oven-sh/bun @ ce9788716f66e2782c0ce5ae46a179fbb9f7c447
PR:   25830

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
SHARED_TS = f"{REPO}/src/js/internal/sql/shared.ts"
SQLITE_TS = f"{REPO}/src/js/internal/sql/sqlite.ts"
MYSQL_TS = f"{REPO}/src/js/internal/sql/mysql.ts"
POSTGRES_TS = f"{REPO}/src/js/internal/sql/postgres.ts"
TEST_CLAUDE_MD = f"{REPO}/test/CLAUDE.md"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------


def test_shared_has_build_function():
    """shared.ts must define and export buildDefinedColumnsAndQuery."""
    script = (
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync('{SHARED_TS}', 'utf8');\n"
        "\n"
        "if (!src.includes('function buildDefinedColumnsAndQuery')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function not defined'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "const exportSection = src.split('export default').pop();\n"
        "if (!exportSection.includes('buildDefinedColumnsAndQuery')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function not exported'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!src.includes('!== \"undefined\"')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'missing undefined check'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!src.includes('definedColumns') || !src.includes('columnsSql')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'missing return fields'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "console.log(JSON.stringify({ok: true}));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data.get("ok"), f"buildDefinedColumnsAndQuery check failed: {data.get('reason', 'unknown')}"


def test_single_insert_no_null_fallback():
    """Single-insert path in sqlite.ts pushes columnValue directly, not converting undefined to null."""
    script = (
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync('{SQLITE_TS}', 'utf8');\n"
        "\n"
        "// Find the SQLCommand.insert section and check the single-item handling\n"
        "const insertSectionStart = src.indexOf('command === SQLCommand.insert');\n"
        "if (insertSectionStart === -1) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'could not find insert section'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "// Get the insert section (from the check onwards)\n"
        "const insertSection = src.substring(insertSectionStart, insertSectionStart + 5000);\n"
        "\n"
        "// Find the single-item else block after the $isArray(items) check\n"
        "const arrayItemsCheck = insertSection.indexOf('$isArray(items)');\n"
        "if (arrayItemsCheck === -1) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no $isArray(items) check found'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "// Get the part after $isArray(items) check - the else block is the single-insert path\n"
        "const afterArrayCheck = insertSection.substring(arrayItemsCheck);\n"
        "\n"
        "// Find the } else { block after the array handling\n"
        "const elseMatch = afterArrayCheck.match(/}\\s*else\\s*{/);\n"
        "if (!elseMatch) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no else block after array handling'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "// Extract the single-insert block (approximate)\n"
        "const elseIndex = afterArrayCheck.indexOf(elseMatch[0]);\n"
        "let singleBlock = afterArrayCheck.substring(elseIndex, elseIndex + 1500);\n"
        "\n"
        "// Check that the single-insert block uses buildDefinedColumnsAndQuery or definedColumns\n"
        "const usesDefinedColumns = singleBlock.includes('definedColumn');\n"
        "\n"
        "// Check for the old undefined-to-null conversion pattern\n"
        "const hasUndefinedNullCheck = singleBlock.includes('typeof columnValue === \"undefined\"') ||\n"
        "                               (singleBlock.includes('=== \"undefined\"') && singleBlock.includes('push(null)'));\n"
        "\n"
        "if (hasUndefinedNullCheck && !usesDefinedColumns) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'single-insert still converts undefined to null'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!usesDefinedColumns) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'single-insert does not use definedColumns'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "console.log(JSON.stringify({ok: true}));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data.get("ok"), f"Single-insert null check failed: {data.get('reason', 'unknown')}"


def test_build_function_checks_all_items():
    """buildDefinedColumnsAndQuery must iterate ALL items to find defined columns (data loss fix)."""
    script = (
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync('{SHARED_TS}', 'utf8');\n"
        "\n"
        "// Use regex to extract the full function including nested braces\n"
        "const funcMatch = src.match(/function buildDefinedColumnsAndQuery[\\s\\S]*?\\{[\\s\\S]*?\\n\\}/);\n"
        "if (!funcMatch) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function not found'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "const funcBody = funcMatch[0];\n"
        "\n"
        "// Check for required patterns - must check ALL items in the array\n"
        "const hasItemsLength = funcBody.includes('items.length');\n"
        "const hasItemsLoop = funcBody.includes('items.length') || funcBody.includes('for (let j = 0; j < items');\n"
        "const hasPerItemCheck = funcBody.includes('typeof items[j][column]') || funcBody.includes('items[j][column]') || funcBody.includes('items[j]');\n"
        "const hasBreak = funcBody.includes('break');\n"
        "\n"
        "if (!hasItemsLoop && !hasItemsLength) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no loop over all items'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!hasPerItemCheck) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no per-item typeof check'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!hasBreak) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no break after finding defined value'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "console.log(JSON.stringify({ok: true}));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data.get("ok"), f"All-items check failed: {data.get('reason', 'unknown')}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - config/documentation update
# ---------------------------------------------------------------------------


def test_claude_md_to_equal_guidance():
    """test/CLAUDE.md must document .toEqual preference for nested/complex object equality."""
    script = (
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync('{TEST_CLAUDE_MD}', 'utf8');\n"
        "\n"
        "if (!src.includes('.toEqual')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no .toEqual mentioned'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "const hasSection = src.toLowerCase().includes('nested') ||\n"
        "                   src.toLowerCase().includes('complex object');\n"
        "if (!hasSection) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no section header for toEqual guidance'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!src.includes('GOOD') && !src.includes('prefer') && !src.includes('always prefer')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no GOOD/prefer example'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!src.includes('.toBe')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no .toBe contrast'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "console.log(JSON.stringify({ok: true}));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data.get("ok"), f"CLAUDE.md toEqual check failed: {data.get('reason', 'unknown')}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub + structural
# ---------------------------------------------------------------------------


def test_not_stub():
    """buildDefinedColumnsAndQuery must have substantial logic, not be a stub."""
    script = (
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync('{SHARED_TS}', 'utf8');\n"
        "\n"
        "// Use regex to extract the full function including nested braces\n"
        "const funcMatch = src.match(/function buildDefinedColumnsAndQuery[\\s\\S]*?\\{[\\s\\S]*?\\n\\}/);\n"
        "if (!funcMatch) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function not found'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "const funcBody = funcMatch[0];\n"
        "\n"
        "// Count lines excluding comments and braces\n"
        "const allLines = funcBody.split('\\n');\n"
        "const lines = allLines.filter(l => {\n"
        "    const trimmed = l.trim();\n"
        "    return trimmed.length > 0 &&\n"
        "           trimmed !== '{' &&\n"
        "           trimmed !== '}' &&\n"
        "           !trimmed.startsWith('//') &&\n"
        "           !trimmed.startsWith('*') &&\n"
        "           !trimmed.startsWith('/*');\n"
        "});\n"
        "\n"
        "const hasForLoop = funcBody.includes('for (');\n"
        "const hasIf = funcBody.includes('if (');\n"
        "\n"
        "if (lines.length < 8) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function has only ' + lines.length + ' logic lines, expected >= 8'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!hasForLoop) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no for loop'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!hasIf) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no conditional logic'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "console.log(JSON.stringify({ok: true, lines: lines.length}));\n"
    )
    result = _run_node(script)
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data.get("ok"), f"Stub check failed: {data.get('reason', 'unknown')}"


def test_all_adapters_import_function():
    """All three SQL adapter files must import buildDefinedColumnsAndQuery from shared."""
    adapters = [
        ("sqlite.ts", SQLITE_TS),
        ("mysql.ts", MYSQL_TS),
        ("postgres.ts", POSTGRES_TS),
    ]
    missing = []
    for name, path in adapters:
        src = Path(path).read_text()
        if "buildDefinedColumnsAndQuery" not in src:
            missing.append(name)
            continue
        # Verify it's imported from internal/sql/shared
        lines = src.split("\n")
        found = False
        for i, line in enumerate(lines):
            if "buildDefinedColumnsAndQuery" in line:
                # Look in surrounding context for the require("internal/sql/shared") call
                context = "\n".join(lines[max(0, i - 5):i + 5])
                if "require" in context and "internal/sql/shared" in context:
                    found = True
                    break
        if not found:
            missing.append(f"{name} (not from shared)")

    assert not missing, f"Adapters missing buildDefinedColumnsAndQuery import: {missing}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks that should pass on base commit
# ---------------------------------------------------------------------------


def test_repo_prettier_format():
    """SQL source files must pass Prettier formatting check (pass_to_pass)."""
    sql_files = [
        f"{REPO}/src/js/internal/sql/shared.ts",
        f"{REPO}/src/js/internal/sql/sqlite.ts",
        f"{REPO}/src/js/internal/sql/mysql.ts",
        f"{REPO}/src/js/internal/sql/postgres.ts",
    ]
    for f in sql_files:
        r = subprocess.run(
            ["npx", "prettier", "--check", f],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed for {f}:\n{r.stderr[-500:]}"


def test_repo_syntax_valid():
    """SQL source files must have valid syntax (esbuild transpilation passes) (pass_to_pass)."""
    sql_files = [
        f"{REPO}/src/js/internal/sql/shared.ts",
        f"{REPO}/src/js/internal/sql/sqlite.ts",
        f"{REPO}/src/js/internal/sql/mysql.ts",
        f"{REPO}/src/js/internal/sql/postgres.ts",
    ]
    r = subprocess.run(
        ["npx", "esbuild", "--loader:.ts=ts", "--outdir=/tmp/esbuild-out"] + sql_files,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"esbuild syntax check failed:\n{r.stderr[-500:]}"


def test_repo_typescript_no_errors():
    """TypeScript files should transpile without errors (pass_to_pass)."""
    # Run esbuild with strictest error checking
    sql_files = [
        f"{REPO}/src/js/internal/sql/shared.ts",
        f"{REPO}/src/js/internal/sql/sqlite.ts",
        f"{REPO}/src/js/internal/sql/mysql.ts",
        f"{REPO}/src/js/internal/sql/postgres.ts",
    ]
    r = subprocess.run(
        ["npx", "esbuild", "--loader:.ts=ts", "--log-level=error", "--outdir=/tmp/esbuild-check"] + sql_files,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript error check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
