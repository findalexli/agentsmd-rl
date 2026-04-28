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
    """Repo oxlint passes on modified SQL files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "src/js/internal/sql/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed: {r.stdout[-1000:]} {r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo prettier check passes on modified SQL files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/js/internal/sql/shared.ts",
         "src/js/internal/sql/sqlite.ts", "src/js/internal/sql/mysql.ts",
         "src/js/internal/sql/postgres.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_git_status():
    """Git repository is properly initialized and functional (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    assert "true" in r.stdout.strip(), "Not inside a valid git work tree"


# [repo_tests] pass_to_pass
def test_repo_oxlint_full():
    """Repo oxlint passes on all src/js (pass_to_pass)."""
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


def _find_matching_paren(text, start):
    """Find the matching closing paren for the opening paren at position start."""
    depth = 0
    for i, c in enumerate(text[start:]):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return start + i
    return -1


def _find_matching_brace(text, start):
    """Find the matching closing brace for the opening brace at position start."""
    depth = 0
    for i, c in enumerate(text[start:]):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return start + i
    return -1


def _find_column_filter_function(text):
    """
    Find a column-filtering function that:
    - Has 3 parameters (columns, items, escapeIdentifier)
    - Returns an object with two properties
    
    Accepts any function name and any generic syntax (or none).
    Does NOT require specific variable names.
    """
    # Find all function declarations with <T> or without
    patterns = [
        r'function\s+(\w+)\s*<T>\s*\(',
        r'function\s+(\w+)\s*\(',
    ]
    
    for pattern in patterns:
        for m in re.finditer(pattern, text):
            func_name = m.group(1)
            
            # Extract params
            paren_start = m.end() - 1
            paren_end = _find_matching_paren(text, paren_start)
            if paren_end < 0:
                continue
            
            params_str = text[paren_start:paren_end + 1]
            
            # Check for required param names (flexible)
            has_columns = 'columns' in params_str.lower()
            has_items = 'items' in params_str.lower()
            has_escape = 'escape' in params_str.lower() or 'identifier' in params_str.lower()
            
            if has_columns and has_items and has_escape:
                return func_name
    
    return None


def _extract_function_body(text, func_name):
    """Extract a function's full body from source text."""
    # Find function declaration
    patterns = [
        rf'function\s+{func_name}\s*<T>\s*\(',
        rf'function\s+{func_name}\s*\(',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        
        func_start = match.start()
        paren_start = match.end() - 1
        
        # Find closing ) of params
        paren_end = _find_matching_paren(text, paren_start)
        if paren_end < 0:
            continue
        
        # Skip past return type annotation: ): { ... }
        # Start after params )
        i = paren_end + 1
        while i < len(text) and text[i] in ' \n\t:':
            i += 1
        
        if i >= len(text):
            continue
        
        # If we're at a {, skip the entire return type object
        if text[i] == '{':
            type_end = _find_matching_brace(text, i)
            if type_end < 0:
                continue
            body_start = type_end + 1
        else:
            # No return type annotation, body starts here
            body_start = i
        
        # Skip whitespace to find function body {
        while body_start < len(text) and text[body_start] in ' \n\t':
            body_start += 1
        
        if body_start >= len(text) or text[body_start] != '{':
            continue
        
        # Find matching } for function body
        body_end = _find_matching_brace(text, body_start)
        if body_end < 0:
            continue
        
        return text[func_start:body_end + 1]
    
    return None


def _jsify_typescript(func_body):
    """Convert TypeScript function body to runnable JavaScript."""
    js = func_body
    js = js.replace("$isArray", "Array.isArray")
    js = re.sub(r"<T>", "", js)
    js = re.sub(r"columns:\s*\(keyof T\)\[\]", "columns", js)
    js = re.sub(r"items:\s*T \| T\[\]", "items", js)
    js = re.sub(r"escapeIdentifier:\s*\(name:\s*string\)\s*=>\s*string", "escapeIdentifier", js)
    js = re.sub(r"\):\s*\{[^}]*\}\s*\{", ") {", js)
    js = re.sub(r"const (\w+):\s*\(keyof T\)\[\]\s*=", r"const \1 =", js)
    js = js.replace(" as string", "")
    js = re.sub(r"\b(keyof T)\b", "string", js)
    return js


def _build_behavioral_test_script(func_name, js_func):
    """
    Build a JavaScript test script that verifies the column-filtering behavior
    without depending on specific variable names from the gold solution.
    """
    test_code = js_func + """

const esc = (name) => '"' + name + '"';
const testFn = eval("FUNC_NAME_PLACEHOLDER");

// Test 1: Single item, all defined - expect 2 columns
(function() {
    var r = testFn(['a', 'b'], { a: 1, b: 2 }, esc);
    var keys = Object.keys(r).filter(function(k) { return Array.isArray(r[k]); });
    var arr = r[keys[0]];
    if (arr.length !== 2) {
        console.error('T1 fail: expected 2 cols, got ' + arr.length);
        process.exit(1);
    }
})();

// Test 2: Single item, one undefined - expect 1 column
(function() {
    var r = testFn(['a', 'b'], { a: 1, b: undefined }, esc);
    var keys = Object.keys(r).filter(function(k) { return Array.isArray(r[k]); });
    var arr = r[keys[0]];
    if (arr.length !== 1) {
        console.error('T2 fail: expected 1 col, got ' + arr.length);
        process.exit(1);
    }
    if (arr[0] !== 'a') {
        console.error('T2 fail: expected col a, got ' + arr[0]);
        process.exit(1);
    }
})();

// Test 3: Bulk insert - first undefined, second defined (DATA LOSS fix)
(function() {
    var r = testFn(['a', 'b'], [{ a: 1, b: undefined }, { a: 2, b: 'val' }], esc);
    var keys = Object.keys(r).filter(function(k) { return Array.isArray(r[k]); });
    var arr = r[keys[0]];
    if (arr.length !== 2) {
        console.error('T3 fail: expected 2 cols, got ' + arr.length);
        process.exit(1);
    }
})();

// Test 4: All undefined - column excluded
(function() {
    var r = testFn(['a', 'b'], [{ a: 1, b: undefined }, { a: 2, b: undefined }], esc);
    var keys = Object.keys(r).filter(function(k) { return Array.isArray(r[k]); });
    var arr = r[keys[0]];
    if (arr.length !== 1) {
        console.error('T4 fail: expected 1 col, got ' + arr.length);
        process.exit(1);
    }
})();

// Test 5: SQL format check - should produce (col1, col2) VALUES format
(function() {
    var r = testFn(['x', 'y'], { x: 1, y: 2 }, esc);
    var keys = Object.keys(r).filter(function(k) { return typeof r[k] === 'string'; });
    var sql = r[keys[0]];
    if (!sql.startsWith('(') || !sql.endsWith(' VALUES')) {
        console.error('T5 fail: bad SQL format: ' + sql);
        process.exit(1);
    }
    if (!sql.includes('"x"') || !sql.includes('"y"')) {
        console.error('T5 fail: missing column names: ' + sql);
        process.exit(1);
    }
})();

// Test 6: Middle item has defined value - column must be included
(function() {
    var r = testFn(['a', 'opt'], [{ a: 1, opt: undefined }, { a: 2, opt: 'mid' }, { a: 3, opt: undefined }], esc);
    var keys = Object.keys(r).filter(function(k) { return Array.isArray(r[k]); });
    var arr = r[keys[0]];
    if (arr.length !== 2) {
        console.error('T6 fail: expected 2 cols, got ' + arr.length);
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
    func_name = _find_column_filter_function(text)
    assert func_name, "Column-filtering function with expected signature not found in shared.ts"

    func_body = _extract_function_body(text, func_name)
    assert func_body, f"Could not extract body for function '{func_name}'"

    js_func = _jsify_typescript(func_body)
    js_code = _build_behavioral_test_script(func_name, js_func)
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


def _check_adapter_imports_and_calls(filepath, adapter_name):
    """
    Verify an adapter file:
    1. Imports the shared module via require("internal/sql/shared")
    2. Calls some function with (columns, items, escapeIdentifier) pattern

    Does NOT check for specific variable names - allows any return value destructuring.
    """
    text = Path(filepath).read_text()

    # Must require the shared module
    require_pattern = r'require\s*\(\s*["\']internal/sql/shared["\']\s*\)'
    assert re.search(require_pattern, text), \
        f"{adapter_name}: does not require internal/sql/shared"

    # Must call some function with columns, items pattern
    call_pattern = r'\w+\s*\(\s*columns\s*,\s*items\s*,'
    assert re.search(call_pattern, text), \
        f"{adapter_name}: does not call any function with columns, items pattern"


# [pr_diff] fail_to_pass
def test_adapters_import_shared_function():
    """All three SQL adapters import and use a shared column-filtering function."""
    adapters = [
        ("sqlite", SQLITE_TS),
        ("mysql", MYSQL_TS),
        ("postgres", POSTGRES_TS),
    ]

    for name, filepath in adapters:
        _check_adapter_imports_and_calls(filepath, name)


# [pr_diff] fail_to_pass
def test_claude_md_toequal_guidance():
    """test/CLAUDE.md must document preference for .toEqual over many .toBe assertions."""
    text = Path(CLAUDE_MD).read_text()
    assert ".toEqual" in text, "test/CLAUDE.md does not mention .toEqual"
    has_nested = "Nested" in text or "nested" in text
    has_complex = "complex object" in text.lower() or "object equality" in text.lower()
    assert has_nested or has_complex, (
        "test/CLAUDE.md missing section about nested/complex object equality"
    )
    assert "toEqual(" in text, "test/CLAUDE.md missing .toEqual usage example"
