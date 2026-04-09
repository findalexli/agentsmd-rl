"""
Task: react-devtools-force-error-crash
Repo: react @ 4610359651fa10247159e2050f8ec222cb7faa91
PR:   35985

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


def _extract_should_error_function():
    """Extract the shouldErrorFiberAccordingToMap function body from renderer.js."""
    src = Path(RENDERER).read_text()
    # Find the function. It starts with "function shouldErrorFiberAccordingToMap"
    # and is indented inside the attach() closure.
    pattern = r"function shouldErrorFiberAccordingToMap\(fiber:\s*any\)[^{]*\{([\s\S]*?)\n  \}"
    m = re.search(pattern, src)
    assert m, "Could not find shouldErrorFiberAccordingToMap function in renderer.js"
    return m.group(0), src


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_unmatched_fiber_returns_null():
    """shouldErrorFiberAccordingToMap must return null (not false) for fibers not in the map."""
    script = r"""
const fs = require('fs');
const src = fs.readFileSync(
    'packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8'
);

// Extract the shouldErrorFiberAccordingToMap function
const funcRegex = /function shouldErrorFiberAccordingToMap\(fiber:\s*any\)[^{]*\{([\s\S]*?)\n  \}/;
const match = src.match(funcRegex);
if (!match) {
    console.error('Function not found');
    process.exit(1);
}
const body = match[1];

// Find the "if (status === undefined)" block and check its return value
const undefinedBlock = body.match(/if\s*\(status\s*===\s*undefined\)\s*\{[\s\S]*?return\s+(\w+)\s*;/);
if (!undefinedBlock) {
    console.error('status === undefined block not found');
    process.exit(1);
}

const returnValue = undefinedBlock[1];
if (returnValue !== 'null') {
    console.error('Expected return null for undefined status, got: return ' + returnValue);
    process.exit(1);
}
console.log('PASS: undefined status returns null');
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO, capture_output=True, timeout=30
    )
    assert r.returncode == 0, (
        f"Unmatched fiber should return null:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


# [pr_diff] fail_to_pass
def test_return_type_nullable():
    """shouldErrorFiberAccordingToMap return type must include null (boolean | null)."""
    script = r"""
const fs = require('fs');
const src = fs.readFileSync(
    'packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8'
);

// Find the function signature with its return type
const sigRegex = /function shouldErrorFiberAccordingToMap\(fiber:\s*any\):\s*([^{]+)\{/;
const match = src.match(sigRegex);
if (!match) {
    console.error('Function signature not found');
    process.exit(1);
}

const returnType = match[1].trim();
if (!returnType.includes('null')) {
    console.error('Return type does not include null: ' + returnType);
    process.exit(1);
}
if (!returnType.includes('boolean')) {
    console.error('Return type does not include boolean: ' + returnType);
    process.exit(1);
}
console.log('PASS: return type is ' + returnType);
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO, capture_output=True, timeout=30
    )
    assert r.returncode == 0, (
        f"Return type must be boolean | null:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


# [pr_diff] fail_to_pass
def test_three_way_return_semantics():
    """The function must distinguish true, false, and null as three separate return paths.

    On the base commit, both 'not in map' and 'toggled off' return false,
    making them indistinguishable. After the fix, 'not in map' returns null.
    """
    script = r"""
const fs = require('fs');
const src = fs.readFileSync(
    'packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8'
);

// Extract the function body
const funcRegex = /function shouldErrorFiberAccordingToMap\(fiber:\s*any\)[^{]*\{([\s\S]*?)\n  \}/;
const match = src.match(funcRegex);
if (!match) {
    console.error('Function not found');
    process.exit(1);
}
const body = match[1];

// Collect all return statements
const returns = [...body.matchAll(/return\s+(\w+)\s*;/g)].map(m => m[1]);

// Must have at least 3 distinct return values: null, true/false from status, etc.
// The critical requirement: 'null' must be one of the return values
if (!returns.includes('null')) {
    console.error('Missing null return. Found returns: ' + returns.join(', '));
    process.exit(1);
}

// 'status' must still be returned for known fibers
if (!returns.includes('status')) {
    console.error('Missing status return. Found returns: ' + returns.join(', '));
    process.exit(1);
}

// 'false' should NOT appear as a bare return value (it should only come through 'status')
const bareReturns = returns.filter(r => r !== 'status');
if (bareReturns.includes('false')) {
    console.error('Found bare "return false" — unknown fibers must return null, not false');
    process.exit(1);
}

console.log('PASS: three-way return semantics (null for unknown, status for known)');
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO, capture_output=True, timeout=30
    )
    assert r.returncode == 0, (
        f"Three-way return semantics broken:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_matched_fiber_returns_status():
    """Fibers explicitly in forceErrorForFibers must still return their status value."""
    func_body, _ = _extract_should_error_function()
    # The function must still have "return status;" for matched fibers
    assert re.search(r"return\s+status\s*;", func_body), (
        "Function must return status for fibers that are in the forceErrorForFibers map"
    )


# [static] pass_to_pass
def test_function_structure_intact():
    """shouldErrorFiberAccordingToMap still exists with core logic (map iteration, status check)."""
    func_body, _ = _extract_should_error_function()
    # Must still iterate over forceErrorForFibers
    assert "forceErrorForFibers" in func_body, (
        "Function must reference forceErrorForFibers map"
    )
    # Must still check status === undefined
    assert re.search(r"status\s*===\s*undefined", func_body), (
        "Function must check for status === undefined"
    )
    # Must still handle setErrorHandler
    assert "setErrorHandler" in func_body, (
        "Function must reference setErrorHandler"
    )
