"""
Task: react-perftrack-bigint-arrays
Repo: facebook/react @ e66ef6480ecd19c6885f2c06dec34fec1fdc0a98
PR:   35648

Arrays containing BigInt values must be classified as COMPLEX_ARRAY in
ReactPerformanceTrackProperties.js, preventing JSON.stringify crashes.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/shared/ReactPerformanceTrackProperties.js"

# Node.js preamble: read source file, strip Flow types, eval to get functions.
_PREAMBLE = r"""
const fs = require('fs');
const assert = require('assert');

// Stubs for ES module imports that get stripped from the source
var isArray = Array.isArray;
var hasOwnProperty = Object.prototype.hasOwnProperty;
var REACT_ELEMENT_TYPE = Symbol('react.element.stub');
var OMITTED_PROP_ERROR = Symbol('omitted');
function getComponentNameFromType() { return 'Unknown'; }

var src = fs.readFileSync('%s', 'utf8');

// Strip ES module syntax
src = src.replace(/^import .+$/gm, '');
src = src.replace(/^export /gm, '');

// Strip Flow type annotations
src = src.replace(/:\s*Object/g, '');
src = src.replace(/:\s*mixed/g, '');
src = src.replace(/:\s*0\s*\|\s*1\s*\|\s*2\s*\|\s*3/g, '');
src = src.replace(/:\s*Array<\[string,\s*string\]>/g, '');
src = src.replace(/:\s*Array<any>/g, '');
src = src.replace(/:\s*any\b/g, '');
src = src.replace(/:\s*number\b/g, '');
src = src.replace(/:\s*string\b/g, '');
src = src.replace(/:\s*void\b/g, '');
src = src.replace(/:\s*boolean\b/g, '');
src = src.replace(/@flow/g, '');

try {
    eval(src);
} catch (e) {
    console.error('Failed to eval cleaned source: ' + e.message);
    process.exit(2);
}
""" % TARGET


def _run_node(test_js: str):
    """Run JS preamble + test code via Node. Fail pytest on non-zero exit."""
    script = _PREAMBLE + "\n" + test_js
    tmp = Path("/tmp/_perftrack_test.js")
    tmp.write_text(script)
    try:
        r = subprocess.run(
            ["node", str(tmp)], capture_output=True, timeout=60, text=True
        )
        if r.returncode != 0:
            pytest.fail(
                f"Node test failed (exit {r.returncode}):\n"
                f"stdout: {r.stdout[:2000]}\nstderr: {r.stderr[:2000]}"
            )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BigInt classification fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bigint_only_array_is_complex():
    """Pure-BigInt arrays like [1n, 2n] must return 'Array' label, not JSON string."""
    _run_node("""
const cases = [[1n, 2n, 3n], [BigInt(0), BigInt(999)], [1n]];
for (const arr of cases) {
    const props = [];
    addValueToProperties('items', arr, props, 0, '');
    const entry = props.find(p => p[0].includes('items'));
    assert.ok(entry, 'No entry found for bigint array [' + arr.map(String) + ']');
    assert.strictEqual(entry[1], 'Array',
        'Expected "Array" for [' + arr.map(String) + '], got "' + entry[1] + '"');
}
""")


# [pr_diff] fail_to_pass
def test_mixed_bigint_array_is_complex():
    """Arrays mixing BigInt with other types must return 'Array', not JSON string."""
    _run_node("""
const cases = [[1, 2n, 3], ['x', 1n], [1n, true]];
for (const arr of cases) {
    const props = [];
    addValueToProperties('data', arr, props, 0, '');
    const entry = props.find(p => p[0].includes('data'));
    assert.ok(entry, 'No entry found for mixed array [' + arr.map(String) + ']');
    assert.strictEqual(entry[1], 'Array',
        'Expected "Array" for [' + arr.map(String) + '], got "' + entry[1] + '"');
}
""")


# [pr_diff] fail_to_pass
def test_no_json_stringify_crash_on_bigint():
    """addValueToProperties must not throw TypeError when array contains BigInt."""
    _run_node("""
const bigintArrays = [
    [0n],
    [BigInt(Number.MAX_SAFE_INTEGER) + 1n],
    [1n, 2n, 3n, 4n, 5n],
    [-1n, 0n, 1n],
];
for (const arr of bigintArrays) {
    const props = [];
    addValueToProperties('val', arr, props, 0, '');
    assert.ok(props.length > 0,
        'No properties added for [' + arr.map(String) + ']');
}
""")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_primitive_array_still_serialized():
    """Non-BigInt primitive arrays must still be JSON-serialized (fix must not regress)."""
    _run_node("""
const cases = [
    {arr: [1, 2, 3], expected: '[1,2,3]'},
    {arr: [true, false], expected: '[true,false]'},
    {arr: [42], expected: '[42]'},
];
for (const {arr, expected} of cases) {
    const props = [];
    addValueToProperties('p', arr, props, 0, '');
    const entry = props.find(e => e[0].includes('p'));
    assert.ok(entry, 'No entry for primitive array ' + JSON.stringify(arr));
    assert.strictEqual(entry[1], expected,
        'Expected ' + expected + ' for ' + JSON.stringify(arr) + ', got ' + entry[1]);
}
""")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# These verify the repo's own lint and test commands pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_shared_package_tests():
    """Repo's shared package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "packages/shared", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Shared package tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
