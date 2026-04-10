"""
Task: bun-sql-undefined-insert-filter
Repo: oven-sh/bun @ ce9788716f66e2782c0ce5ae46a179fbb9f7c447
PR:   25830

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
SHARED_TS = f"{REPO}/src/js/internal/sql/shared.ts"
SQLITE_TS = f"{REPO}/src/js/internal/sql/sqlite.ts"
MYSQL_TS = f"{REPO}/src/js/internal/sql/mysql.ts"
POSTGRES_TS = f"{REPO}/src/js/internal/sql/postgres.ts"
CLAUDE_MD = f"{REPO}/test/CLAUDE.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be syntactically valid (balanced braces)."""
    for filepath in [SHARED_TS, SQLITE_TS, MYSQL_TS, POSTGRES_TS]:
        p = Path(filepath)
        assert p.exists(), f"{filepath} does not exist"
        text = p.read_text()
        assert text.count("{") > 0, f"{filepath} appears empty"
        depth = 0
        for ch in text:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            if depth < 0:
                break
        assert depth == 0, f"{filepath} has unbalanced braces (depth={depth})"


# [repo_tests] pass_to_pass
def test_repo_oxlint():
    """Repo's oxlint passes on modified SQL files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "src/js/internal/sql/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed: {r.stdout[-1000:]} {r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's prettier check passes on modified SQL files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/js/internal/sql/shared.ts",
         "src/js/internal/sql/sqlite.ts", "src/js/internal/sql/mysql.ts",
         "src/js/internal/sql/postgres.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed: {r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_undefined_filtering_behavior():
    """Extracted buildDefinedColumnsAndQuery filters undefined columns correctly."""
    text = Path(SHARED_TS).read_text()

    # Find and extract the function
    match = re.search(
        r"function buildDefinedColumnsAndQuery[^{]*\{[^}]+\}\s*\{",
        text,
        re.DOTALL
    )
    assert match, "buildDefinedColumnsAndQuery not found in shared.ts"
    
    start = match.start()
    
    # Extract full function body by tracking braces from the actual body start
    # The regex matched up to the opening brace after the return type
    body_start = match.end() - 1  # Position of the actual function body opening brace
    
    depth = 0
    in_func = False
    end = start
    for i in range(body_start, len(text)):
        if text[i] == "{":
            depth += 1
            in_func = True
        elif text[i] == "}":
            depth -= 1
        if in_func and depth == 0:
            end = i + 1
            break

    func_body = text[start:end]

    # Strip TypeScript → valid JavaScript
    func_body = func_body.replace("$isArray", "Array.isArray")
    func_body = re.sub(r"<T>", "", func_body)
    func_body = re.sub(r"columns:\s*\(keyof T\)\[\]", "columns", func_body)
    func_body = re.sub(r"items:\s*T \| T\[\]", "items", func_body)
    func_body = re.sub(
        r"escapeIdentifier:\s*\(name:\s*string\)\s*=>\s*string",
        "escapeIdentifier",
        func_body,
    )
    # Handle multiline return type annotation with re.DOTALL
    func_body = re.sub(
        r"\):\s*\{[^}]+definedColumns[^}]+columnsSql[^}]+\}\s*\{",
        ") {",
        func_body,
        flags=re.DOTALL,
    )
    func_body = re.sub(
        r"const definedColumns:\s*\(keyof T\)\[\]\s*=",
        "const definedColumns =",
        func_body,
    )
    func_body = func_body.replace(" as string", "")

    test_script = func_body + r"""
const esc = (name) => '"' + name + '"';

// Test 1: Single item, all defined → both columns included
{
    const r = buildDefinedColumnsAndQuery(['a', 'b'], { a: 1, b: 2 }, esc);
    if (r.definedColumns.length !== 2) {
        console.error('T1 fail: expected 2 cols, got ' + r.definedColumns.length);
        process.exit(1);
    }
}

// Test 2: Single item, one undefined → filtered out
{
    const r = buildDefinedColumnsAndQuery(['a', 'b'], { a: 1, b: undefined }, esc);
    if (r.definedColumns.length !== 1) {
        console.error('T2 fail: expected 1 col, got ' + r.definedColumns.length);
        process.exit(1);
    }
    if (r.definedColumns[0] !== 'a') {
        console.error('T2 fail: expected col a, got ' + r.definedColumns[0]);
        process.exit(1);
    }
}

// Test 3: Bulk insert — first item undefined, second defined (DATA LOSS fix)
{
    const r = buildDefinedColumnsAndQuery(
        ['a', 'b'],
        [{ a: 1, b: undefined }, { a: 2, b: 'val' }],
        esc,
    );
    if (r.definedColumns.length !== 2) {
        console.error('T3 fail: expected 2 cols (b defined in 2nd item), got ' + r.definedColumns.length);
        process.exit(1);
    }
}

// Test 4: All undefined across all items → column excluded
{
    const r = buildDefinedColumnsAndQuery(
        ['a', 'b'],
        [{ a: 1, b: undefined }, { a: 2, b: undefined }],
        esc,
    );
    if (r.definedColumns.length !== 1) {
        console.error('T4 fail: expected 1 col, got ' + r.definedColumns.length);
        process.exit(1);
    }
}

// Test 5: SQL format — columns wrapped and ends with VALUES
{
    const r = buildDefinedColumnsAndQuery(['x', 'y'], { x: 1, y: 2 }, esc);
    if (!r.columnsSql.startsWith('(') || !r.columnsSql.endsWith(') VALUES')) {
        console.error('T5 fail: bad columnsSql: ' + r.columnsSql);
        process.exit(1);
    }
    if (!r.columnsSql.includes('"x"') || !r.columnsSql.includes('"y"')) {
        console.error('T5 fail: missing column names: ' + r.columnsSql);
        process.exit(1);
    }
}

// Test 6: Middle item in 3-item bulk has defined value → column included
{
    const r = buildDefinedColumnsAndQuery(
        ['a', 'opt'],
        [{ a: 1, opt: undefined }, { a: 2, opt: 'mid' }, { a: 3, opt: undefined }],
        esc,
    );
    if (r.definedColumns.length !== 2) {
        console.error('T6 fail: expected 2 cols, got ' + r.definedColumns.length);
        process.exit(1);
    }
}

console.log('PASS');
"""

    script_path = Path(REPO) / "_eval_test_undefined.js"
    script_path.write_text(test_script)
    try:
        result = subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=30,
        )
    finally:
        script_path.unlink(missing_ok=True)

    assert result.returncode == 0, f"Behavioral tests failed:\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_adapters_import_shared_function():
    """All three SQL adapters must import and use buildDefinedColumnsAndQuery."""
    for name, filepath in [("sqlite", SQLITE_TS), ("mysql", MYSQL_TS), ("postgres", POSTGRES_TS)]:
        text = Path(filepath).read_text()
        assert "buildDefinedColumnsAndQuery" in text, (
            f"{name}.ts does not import buildDefinedColumnsAndQuery"
        )
        assert "definedColumns" in text, (
            f"{name}.ts does not use definedColumns from the shared function"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/doc update tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_claude_md_toequal_guidance():
    """test/CLAUDE.md must document preference for .toEqual over many .toBe assertions."""
    text = Path(CLAUDE_MD).read_text()
    assert ".toEqual" in text, (
        "test/CLAUDE.md does not mention .toEqual"
    )
    assert "Nested" in text or "complex object" in text.lower() or "object equality" in text.lower(), (
        "test/CLAUDE.md missing section about nested/complex object equality"
    )
    assert "toEqual(" in text, (
        "test/CLAUDE.md missing .toEqual usage example"
    )
