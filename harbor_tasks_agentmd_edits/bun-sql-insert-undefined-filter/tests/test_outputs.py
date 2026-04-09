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
        "// Find the single-insert else branch\n"
        "const lines = src.split('\\n');\n"
        "let inSingleInsert = false;\n"
        "let singleInsertBlock = [];\n"
        "let braceDepth = 0;\n"
        "\n"
        "for (let i = 0; i < lines.length; i++) {\n"
        "    const line = lines[i];\n"
        "    if (line.includes('} else {') && i > 0 && lines[i-1].includes('query += \")\"')) {\n"
        "        inSingleInsert = true;\n"
        "        braceDepth = 0;\n"
        "        continue;\n"
        "    }\n"
        "    if (inSingleInsert) {\n"
        "        singleInsertBlock.push(line);\n"
        "        if (line.includes('{')) braceDepth++;\n"
        "        if (line.includes('}')) {\n"
        "            braceDepth--;\n"
        "            if (braceDepth < 0) {\n"
        "                inSingleInsert = false;\n"
        "                break;\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}\n"
        "\n"
        "const block = singleInsertBlock.join('\\n');\n"
        "\n"
        "const hasUndefinedNullCheck = block.includes('typeof columnValue === \"undefined\"') &&\n"
        "                               block.includes('binding_values.push(null)');\n"
        "\n"
        "if (hasUndefinedNullCheck) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'single-insert still converts undefined to null'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!block.includes('definedColumn')) {\n"
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
        "const funcStart = src.indexOf('function buildDefinedColumnsAndQuery');\n"
        "if (funcStart === -1) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function not found'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "const bodyStart = src.indexOf('{', funcStart);\n"
        "let depth = 0;\n"
        "let funcEnd = -1;\n"
        "for (let i = bodyStart; i < src.length; i++) {\n"
        "    if (src[i] === '{') depth++;\n"
        "    if (src[i] === '}') {\n"
        "        depth--;\n"
        "        if (depth === 0) { funcEnd = i; break; }\n"
        "    }\n"
        "}\n"
        "\n"
        "const funcBody = src.substring(funcStart, funcEnd + 1);\n"
        "\n"
        "if (!funcBody.includes('items.length')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no loop over all items'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!funcBody.includes('typeof items[j][column]')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no per-item typeof check'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!funcBody.includes('break')) {\n"
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
        "const funcStart = src.indexOf('function buildDefinedColumnsAndQuery');\n"
        "if (funcStart === -1) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function not found'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "const bodyStart = src.indexOf('{', funcStart);\n"
        "let depth = 0;\n"
        "let funcEnd = -1;\n"
        "for (let i = bodyStart; i < src.length; i++) {\n"
        "    if (src[i] === '{') depth++;\n"
        "    if (src[i] === '}') {\n"
        "        depth--;\n"
        "        if (depth === 0) { funcEnd = i; break; }\n"
        "    }\n"
        "}\n"
        "\n"
        "const funcBody = src.substring(funcStart, funcEnd + 1);\n"
        "\n"
        "const lines = funcBody.split('\\n').filter(l => {\n"
        "    const trimmed = l.trim();\n"
        "    return trimmed.length > 0 &&\n"
        "           trimmed !== '{' &&\n"
        "           trimmed !== '}' &&\n"
        "           !trimmed.startsWith('//') &&\n"
        "           !trimmed.startsWith('*') &&\n"
        "           !trimmed.startsWith('/*');\n"
        "});\n"
        "\n"
        "if (lines.length < 8) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'function has only ' + lines.length + ' logic lines, expected >= 8'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!funcBody.includes('for (')) {\n"
        "    console.log(JSON.stringify({ok: false, reason: 'no for loop'}));\n"
        "    process.exit(0);\n"
        "}\n"
        "\n"
        "if (!funcBody.includes('if (')) {\n"
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
    """SQL source files must have valid syntax (balanced braces) (pass_to_pass)."""
    sql_files = [
        ("shared.ts", SHARED_TS),
        ("sqlite.ts", SQLITE_TS),
        ("mysql.ts", MYSQL_TS),
        ("postgres.ts", POSTGRES_TS),
    ]
    for name, path in sql_files:
        src = Path(path).read_text()
        # Check for balanced braces
        depth = 0
        for char in src:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth < 0:
                    assert False, f"{name}: Unbalanced braces (extra closing brace)"
        if depth != 0:
            assert False, f"{name}: Unbalanced braces ({depth} unclosed)"
