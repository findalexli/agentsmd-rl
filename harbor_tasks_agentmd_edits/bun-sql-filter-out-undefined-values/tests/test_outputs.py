"""
Task: bun-sql-filter-out-undefined-values
Repo: oven-sh/bun @ ce9788716f66e2782c0ce5ae46a179fbb9f7c447
PR:   25830

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_build_defined_columns_fn():
    """Extract buildDefinedColumnsAndQuery from shared.ts and return as valid JS."""
    shared = Path(REPO) / "src" / "js" / "internal" / "sql" / "shared.ts"
    assert shared.exists(), "shared.ts must exist"
    content = shared.read_text()

    # Find the function start
    match = re.search(
        r'(function\s+buildDefinedColumnsAndQuery)',
        content,
    )
    assert match, "buildDefinedColumnsAndQuery function not found in shared.ts"

    # Extract full function body by counting braces
    start = match.start()
    brace_count = 0
    fn_end = None
    for j in range(start, len(content)):
        if content[j] == '{':
            brace_count += 1
        elif content[j] == '}':
            brace_count -= 1
            if brace_count == 0:
                fn_end = j + 1
                break
    assert fn_end is not None, "Could not find end of buildDefinedColumnsAndQuery"
    fn_text = content[start:fn_end]

    # Strip TypeScript generics and type annotations
    fn_text = re.sub(r'<\w+>', '', fn_text)
    # Remove return type annotation between ): and opening {
    fn_text = re.sub(r'\)\s*:\s*\{[^}]+\}\s*\{', ') {', fn_text, count=1)
    # Remove parameter type annotations
    fn_text = re.sub(r'columns\s*:\s*\([^)]*\)\[\]', 'columns', fn_text)
    fn_text = re.sub(r'items\s*:\s*\w+\s*\|\s*\w+\[\]', 'items', fn_text)
    fn_text = re.sub(r'escapeIdentifier\s*:\s*\([^)]*\)\s*=>\s*\w+', 'escapeIdentifier', fn_text)
    # Remove variable type annotations like `: (keyof T)[]`
    fn_text = re.sub(r':\s*\(keyof \w+\)\[\]', '', fn_text)
    # Remove `as string` casts
    fn_text = re.sub(r'\s+as\s+string', '', fn_text)
    # Replace $isArray with Array.isArray
    fn_text = fn_text.replace('$isArray', 'Array.isArray')

    return fn_text


def _run_node(script):
    """Run a Node.js script, return (stdout, stderr, returncode)."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        timeout=10,
    )
    return r.stdout.decode(), r.stderr.decode(), r.returncode


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces (basic syntax)."""
    files = [
        "src/js/internal/sql/shared.ts",
        "src/js/internal/sql/sqlite.ts",
        "src/js/internal/sql/mysql.ts",
        "src/js/internal/sql/postgres.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        opens = content.count('{')
        closes = content.count('}')
        assert opens == closes, f"{f}: unbalanced braces ({opens} open, {closes} close)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_defined_columns_filters_undefined():
    """buildDefinedColumnsAndQuery filters out columns where value is undefined."""
    fn_js = _extract_build_defined_columns_fn()
    script = f"""
{fn_js}

const esc = (name) => '"' + name + '"';
const result = buildDefinedColumnsAndQuery(
    ['id', 'name', 'optional'],
    {{ id: 1, name: 'test', optional: undefined }},
    esc
);

// 'optional' should be filtered out since it's undefined
const out = JSON.stringify(result);
console.log(out);

if (result.definedColumns.length !== 2) {{
    process.exit(1);
}}
if (result.definedColumns.includes('optional')) {{
    process.exit(1);
}}
if (!result.definedColumns.includes('id') || !result.definedColumns.includes('name')) {{
    process.exit(1);
}}
if (!result.columnsSql.includes('"id"') || !result.columnsSql.includes('"name"')) {{
    process.exit(1);
}}
if (result.columnsSql.includes('"optional"')) {{
    process.exit(1);
}}
"""
    stdout, stderr, rc = _run_node(script)
    assert rc == 0, (
        f"buildDefinedColumnsAndQuery should filter undefined columns.\n"
        f"stdout: {stdout}\nstderr: {stderr}"
    )
    data = json.loads(stdout.strip())
    assert len(data["definedColumns"]) == 2
    assert "optional" not in data["definedColumns"]


# [pr_diff] fail_to_pass
def test_build_defined_columns_bulk_union():
    """Bulk insert checks ALL items for defined columns, not just the first."""
    fn_js = _extract_build_defined_columns_fn()
    script = f"""
{fn_js}

const esc = (name) => '"' + name + '"';

// First item has optional=undefined, second has optional="value"
// The column MUST be included because at least one item has a defined value
const result = buildDefinedColumnsAndQuery(
    ['id', 'name', 'optional'],
    [
        {{ id: 1, name: 'a', optional: undefined }},
        {{ id: 2, name: 'b', optional: 'has-value' }},
    ],
    esc
);

const out = JSON.stringify(result);
console.log(out);

// All 3 columns should be included since 'optional' is defined in 2nd item
if (result.definedColumns.length !== 3) {{
    process.exit(1);
}}
if (!result.definedColumns.includes('optional')) {{
    process.exit(1);
}}
if (!result.columnsSql.includes('"optional"')) {{
    process.exit(1);
}}

// Also test: 3 items, only middle one has value
const result2 = buildDefinedColumnsAndQuery(
    ['id', 'name', 'optional'],
    [
        {{ id: 1, name: 'a', optional: undefined }},
        {{ id: 2, name: 'b', optional: 'middle-value' }},
        {{ id: 3, name: 'c', optional: undefined }},
    ],
    esc
);
if (result2.definedColumns.length !== 3) {{
    console.error('Failed 3-item test: expected 3 columns, got', result2.definedColumns.length);
    process.exit(1);
}}
"""
    stdout, stderr, rc = _run_node(script)
    assert rc == 0, (
        f"buildDefinedColumnsAndQuery should check ALL items for defined columns.\n"
        f"stdout: {stdout}\nstderr: {stderr}"
    )
    data = json.loads(stdout.strip())
    assert len(data["definedColumns"]) == 3, "All 3 columns should be present when 2nd item defines 'optional'"
    assert "optional" in data["definedColumns"]


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — test/CLAUDE.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention .toEqual as the preferred assertion
    assert ".toequal" in text, (
        "test/CLAUDE.md should recommend .toEqual for nested object assertions"
    )
    # Must contrast with .toBe (showing what NOT to do)
    assert ".tobe" in text, (
        "test/CLAUDE.md should mention .toBe as the less-preferred alternative"
    )
    # Must be about nested/complex objects specifically
    has_context = (
        "nested" in text
        or "complex object" in text
        or "object equality" in text
    )
    assert has_context, (
        "test/CLAUDE.md should describe this guidance in the context of "
        "nested or complex object equality"
    )


# [config_edit] fail_to_pass

    # Must have example code showing the preferred pattern
    # The good example should use .toEqual with an array/object literal
    assert "expect(" in content and ".toEqual([" in content, (
        "test/CLAUDE.md should include a code example using .toEqual with "
        "an array or object literal"
    )
    # Must have the bad pattern (multiple .toBe calls)
    toBe_count = content.count(".toBe(")
    assert toBe_count >= 2, (
        "test/CLAUDE.md should show a bad example with multiple .toBe assertions"
    )
