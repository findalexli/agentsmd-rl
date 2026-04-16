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


# [repo_tests] pass_to_pass
def test_repo_git_status():
    """Git repo is clean at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_oxlint_full():
    """Repo's oxlint passes on all src/js (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "src/js"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed with errors: {r.stdout[-1000:]} {r.stderr[-500:]}"


# [static] pass_to_pass
def test_ts_syntax_valid():
    """TypeScript files are readable and non-empty (pass_to_pass)."""
    for filepath in [SHARED_TS, SQLITE_TS, MYSQL_TS, POSTGRES_TS]:
        p = Path(filepath)
        assert p.exists(), f"{filepath} does not exist"
        text = p.read_text()
        assert len(text) > 100, f"{filepath} appears too small"
        assert "import" in text or "export" in text or "function" in text, f"{filepath} missing expected TypeScript keywords"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------


def _find_columns_function(text):
    """
    Find any function that matches the expected signature for column filtering.
    Uses flexible pattern matching to support alternative function names.
    The function must:
    - Be a generic function <T>
    - Have 3 parameters where one is an array, one is T|T[], one is a function
    - Return an object with two properties for columns list and SQL fragment
    """
    # Pattern: function name<T>(...params...): { ...definedColumns...columnsSql... } {
    # Uses non-greedy matching to find the function with correct return type
    pattern = r"function\s+(\w+)\s*<T>\s*\([\s\S]*?columns[\s\S]*?items[\s\S]*?escapeIdentifier[\s\S]*?\)\s*:\s*\{[\s\S]*?definedColumns[\s\S]*?columnsSql[\s\S]*?\}\s*\{"
    match = re.search(pattern, text)
    if not match:
        return None, None
    func_name = match.group(1)
    start = match.start()
    body_start = match.end() - 1
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
    return func_name, func_body


def _jsify_typescript(func_body):
    """Convert TypeScript function body to runnable JavaScript."""
    js = func_body
    js = js.replace("$isArray", "Array.isArray")
    js = re.sub(r"<T>", "", js)
    js = re.sub(r"columns:\s*\(keyof T\)\[\]", "columns", js)
    js = re.sub(r"items:\s*T \| T\[\]", "items", js)
    js = re.sub(r"escapeIdentifier:\s*\(name:\s*string\)\s*=>\s*string", "escapeIdentifier", js)
    js = re.sub(r"\):\s*\{[^}]*definedColumns[^}]*columnsSql[^}]*\}\s*\{", ") {", js, flags=re.DOTALL)
    js = re.sub(r"const definedColumns:\s*\(keyof T\)\[\]\s*=", "const definedColumns =", js)
    js = js.replace(" as string", "")
    return js


def _build_test_script(func_name, js_func):
    """Build the JavaScript test script with proper function name handling."""
    test_code = js_func + """

const esc = (name) => '"' + name + '"';
const testFn = eval("FUNC_NAME_PLACEHOLDER");

// Test 1: Single item, all defined
(function() {
    var r = testFn(['a', 'b'], { a: 1, b: 2 }, esc);
    if (r.definedColumns.length !== 2) {
        console.error('T1 fail: expected 2 cols, got ' + r.definedColumns.length);
        process.exit(1);
    }
})();

// Test 2: Single item, one undefined
(function() {
    var r = testFn(['a', 'b'], { a: 1, b: undefined }, esc);
    if (r.definedColumns.length !== 1) {
        console.error('T2 fail: expected 1 col, got ' + r.definedColumns.length);
        process.exit(1);
    }
    if (r.definedColumns[0] !== 'a') {
        console.error('T2 fail: expected col a, got ' + r.definedColumns[0]);
        process.exit(1);
    }
})();

// Test 3: Bulk insert - first undefined, second defined (DATA LOSS fix)
(function() {
    var r = testFn(['a', 'b'], [{ a: 1, b: undefined }, { a: 2, b: 'val' }], esc);
    if (r.definedColumns.length !== 2) {
        console.error('T3 fail: expected 2 cols, got ' + r.definedColumns.length);
        process.exit(1);
    }
})();

// Test 4: All undefined - column excluded
(function() {
    var r = testFn(['a', 'b'], [{ a: 1, b: undefined }, { a: 2, b: undefined }], esc);
    if (r.definedColumns.length !== 1) {
        console.error('T4 fail: expected 1 col, got ' + r.definedColumns.length);
        process.exit(1);
    }
})();

// Test 5: SQL format check
(function() {
    var r = testFn(['x', 'y'], { x: 1, y: 2 }, esc);
    if (!r.columnsSql.startsWith('(') || !r.columnsSql.endsWith(') VALUES')) {
        console.error('T5 fail: bad columnsSql: ' + r.columnsSql);
        process.exit(1);
    }
    if (!r.columnsSql.includes('"x"') || !r.columnsSql.includes('"y"')) {
        console.error('T5 fail: missing column names: ' + r.columnsSql);
        process.exit(1);
    }
})();

// Test 6: Middle item has defined value
(function() {
    var r = testFn(['a', 'opt'], [{ a: 1, opt: undefined }, { a: 2, opt: 'mid' }, { a: 3, opt: undefined }], esc);
    if (r.definedColumns.length !== 2) {
        console.error('T6 fail: expected 2 cols, got ' + r.definedColumns.length);
        process.exit(1);
    }
})();

console.log('PASS');
"""
    test_code = test_code.replace("FUNC_NAME_PLACEHOLDER", func_name)
    return test_code


# [pr_diff] fail_to_pass
def test_undefined_filtering_behavior():
    """The shared column-filtering function correctly filters undefined columns."""
    text = Path(SHARED_TS).read_text()
    func_name, func_body = _find_columns_function(text)
    assert func_body, "Column-filtering function with expected signature not found in shared.ts"
    js_func = _jsify_typescript(func_body)
    js_code = _build_test_script(func_name, js_func)
    script_path = Path(REPO) / "_eval_test_undefined.js"
    script_path.write_text(js_code)
    try:
        result = subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=30,
        )
    finally:
        script_path.unlink(missing_ok=True)
    assert result.returncode == 0, f"Behavioral tests failed:\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS, got: {result.stdout}"


def _extract_and_run_adapter_insert(filepath, adapter_name):
    """Extract and run adapter INSERT logic test."""
    text = Path(filepath).read_text()

    # Look for any pattern where a function is called with columns and items
    # Flexible pattern: any function call with columns, items, and escapeIdentifier
    pattern = r'(?:const|let|var)\s+\{\s*(\w+)\s*,\s*(\w+)\s*\}\s*=\s*(\w+)\s*\(\s*columns\s*,\s*items\s*,'
    match = re.search(pattern, text)
    if not match:
        return False, f"{adapter_name}: could not find function call pattern with columns, items"
    result_var1, result_var2, func_name = match.groups()

    # Verify the function is imported from shared
    require_pattern = r'require\s*\(\s*["\']internal/sql/shared["\']\s*\)'
    if not re.search(require_pattern, text):
        return False, f"{adapter_name}: does not require internal/sql/shared"

    # Build test script - use the extracted function name
    test_script = r"""
// Mock buildDefinedColumnsAndQuery
function buildDefinedColumnsAndQuery(columns, items, escapeIdentifier) {
    var definedColumns = [];
    var columnsSql = "(";
    var columnCount = columns.length;
    for (var k = 0; k < columnCount; k++) {
        var column = columns[k];
        var hasDefinedValue = false;
        if (Array.isArray(items)) {
            for (var j = 0; j < items.length; j++) {
                if (typeof items[j][column] !== 'undefined') {
                    hasDefinedValue = true;
                    break;
                }
            }
        } else {
            hasDefinedValue = typeof items[column] !== 'undefined';
        }
        if (hasDefinedValue) {
            if (definedColumns.length > 0) columnsSql += ", ";
            columnsSql += escapeIdentifier(column);
            definedColumns.push(column);
        }
    }
    columnsSql += ") VALUES";
    return { definedColumns: definedColumns, columnsSql: columnsSql };
}

// Test cases
var esc = function(name) { return '"' + name + '"'; };

// Test 1: Bulk insert with first item undefined, second defined
var items1 = [{ a: 1, b: undefined }, { a: 2, b: 'val' }];
var columns1 = ['a', 'b'];
var r1 = buildDefinedColumnsAndQuery(columns1, items1, esc);
if (r1.definedColumns.length !== 2) {
    console.error('FAIL: expected 2 cols, got ' + r1.definedColumns.length);
    process.exit(1);
}
if (r1.definedColumns[1] !== 'b') {
    console.error('FAIL: expected col b to be defined, got ' + r1.definedColumns[1]);
    process.exit(1);
}

// Test 2: Single item with undefined column
var items2 = { a: 1, b: undefined };
var columns2 = ['a', 'b'];
var r2 = buildDefinedColumnsAndQuery(columns2, items2, esc);
if (r2.definedColumns.length !== 1) {
    console.error('FAIL: expected 1 col after filtering undefined, got ' + r2.definedColumns.length);
    process.exit(1);
}

console.log('ADAPTER_""" + adapter_name + """_PASS');
"""
    return True, test_script


# [pr_diff] fail_to_pass
def test_adapters_import_shared_function():
    """All three SQL adapters import and use a shared column-filtering function."""
    adapters = [
        ("sqlite", SQLITE_TS),
        ("mysql", MYSQL_TS),
        ("postgres", POSTGRES_TS),
    ]
    all_passed = True
    failures = []
    for name, filepath in adapters:
        text = Path(filepath).read_text()
        shared_require = r'require\s*\(\s*["\']internal/sql/shared["\']\s*\)'
        if not re.search(shared_require, text):
            failures.append(f"{name}: does not require internal/sql/shared")
            all_passed = False
            continue

        # Check for function call pattern - flexible about variable names
        func_call_pattern = r'(?:const|let|var)\s+\{\s*\w+\s*,\s*\w+\s*\}\s*=\s*\w+\s*\(\s*columns\s*,\s*items\s*,'
        if not re.search(func_call_pattern, text):
            failures.append(f"{name}: does not call function with columns, items pattern")
            all_passed = False
            continue

        # Also verify escapeIdentifier is passed as third argument
        escape_pattern = r'columns\s*,\s*items\s*,\s*this\.escapeIdentifier\.bind\s*\(\s*this\s*\)'
        if not re.search(escape_pattern, text):
            failures.append(f"{name}: does not pass escapeIdentifier correctly")
            all_passed = False
            continue

        passed, result = _extract_and_run_adapter_insert(filepath, name)
        if not passed:
            failures.append(result)
            all_passed = False
            continue
        script_path = Path(REPO) / f"_eval_test_adapter_{name}.js"
        script_path.write_text(result)
        try:
            proc_result = subprocess.run(
                ["node", str(script_path)],
                capture_output=True, text=True, timeout=30,
            )
            if proc_result.returncode != 0:
                failures.append(f"{name}: behavioral test failed: {proc_result.stderr}")
                all_passed = False
            elif f"ADAPTER_{name}_PASS" not in proc_result.stdout:
                failures.append(f"{name}: did not produce expected output")
                all_passed = False
        finally:
            script_path.unlink(missing_ok=True)
    assert all_passed, f"Adapter tests failed:\n" + "\n".join(failures)


# [pr_diff] fail_to_pass
def test_claude_md_toequal_guidance():
    """test/CLAUDE.md must document preference for .toEqual over many .toBe assertions."""
    text = Path(CLAUDE_MD).read_text()
    assert ".toEqual" in text, "test/CLAUDE.md does not mention .toEqual"
    # Check for nested/complex object equality section (flexible on exact wording)
    has_nested = "Nested" in text or "nested" in text
    has_complex = "complex object" in text.lower() or "object equality" in text.lower()
    assert has_nested or has_complex, (
        "test/CLAUDE.md missing section about nested/complex object equality"
    )
    assert "toEqual(" in text, "test/CLAUDE.md missing .toEqual usage example"
