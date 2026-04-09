"""
Task: react-noop-recoverable-error-console
Repo: react @ 23b2d8514f13f109b980b0a1f4f3aab906ad51d0
PR:   35948

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_on_recoverable_error_calls_console_error():
    """onRecoverableError in noop renderer must actively call console.error with the error."""
    script = r"""
const fs = require('fs');
const source = fs.readFileSync(process.argv[1], 'utf8');

// Find onRecoverableError function body
const match = source.match(/function\s+onRecoverableError\s*\([^)]*\)[^{]*\{([\s\S]*?)\n\s*\}/);
if (!match) { process.stderr.write('Function not found'); process.exit(1); }
const body = match[1];

// Filter out comment-only lines to get active code
const activeLines = body.split('\n').filter(l => {
    const t = l.trim();
    return t && !t.startsWith('//') && !t.startsWith('*');
});

if (activeLines.length === 0) {
    process.stderr.write('Function body has no active statements');
    process.exit(1);
}

if (!activeLines.some(l => l.includes('console.error'))) {
    process.stderr.write('No active console.error call found in function body');
    process.exit(1);
}

// Behavioral check: execute the extracted function body and verify
// console.error is called with the error argument.
const testError = new Error('test-recoverable-error');
let receivedArgs = null;
const savedConsoleError = console.error;
console.error = function(...args) { receivedArgs = args; };
try {
    new Function('error', activeLines.join('\n'))(testError);
} catch(e) {
    // eslint comments may cause issues in eval, but console.error should
    // still be called before any throw
}
console.error = savedConsoleError;

if (!receivedArgs) {
    process.stderr.write('console.error was not called when function executed');
    process.exit(1);
}

// Verify the error argument was actually passed through
if (receivedArgs[0] !== testError) {
    process.stderr.write('console.error was called but did not receive the error argument');
    process.exit(1);
}
"""
    r = subprocess.run(
        ["node", "-e", script,
         f"{REPO}/packages/react-noop-renderer/src/createReactNoop.js"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        "onRecoverableError must actively call console.error with the error — "
        f"node output:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_usememo_test_imports_assert_console_error_dev():
    """useMemoCache test must import and call assertConsoleErrorDev for recoverable errors."""
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');

// Check 1: assertConsoleErrorDev is assigned from internal-test-utils
// (either via destructured require or property access on the module)
const hasImport = /assertConsoleErrorDev\s*=\s*\w+\.assertConsoleErrorDev/.test(content);
if (!hasImport) {
    process.stderr.write('assertConsoleErrorDev is not imported from internal-test-utils');
    process.exit(1);
}

// Check 2: assertConsoleErrorDev is called as a function (not just declared)
const callMatches = content.match(/assertConsoleErrorDev\s*\(\[/g);
if (!callMatches || callMatches.length === 0) {
    process.stderr.write('assertConsoleErrorDev is imported but never called');
    process.exit(1);
}

// Check 3: The call includes the expected concurrent rendering error message
if (!content.includes('There was an error during concurrent rendering')) {
    process.stderr.write('assertConsoleErrorDev call missing expected concurrent rendering error');
    process.exit(1);
}

// Behavioral: verify the import line is syntactically valid JS by attempting
// to create a function from the import pattern
try {
    const importLine = content.match(
        /assertConsoleErrorDev\s*=\s*\w+\.assertConsoleErrorDev[^;\n]*/g
    );
    if (importLine) {
        new Function('InternalTestUtils', 'let assertConsoleErrorDev; ' + importLine[0] + ';');
    }
} catch (e) {
    process.stderr.write('Import line is not valid JS: ' + e.message);
    process.exit(1);
}
"""
    r = subprocess.run(
        ["node", "-e", script,
         f"{REPO}/packages/react-reconciler/src/__tests__/useMemoCache-test.js"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        "useMemoCache-test.js must import and call assertConsoleErrorDev — "
        f"node output:\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_no_spylonDev_console_error():
    """Old spyOnDev(console, 'error') pattern should be removed from useMemoCache test."""
    content = Path(
        f"{REPO}/packages/react-reconciler/src/__tests__/useMemoCache-test.js"
    ).read_text()
    assert "spyOnDev(console, 'error')" not in content, (
        "Old spyOnDev(console, 'error') should be replaced with assertConsoleErrorDev"
    )


# [static] pass_to_pass
def test_source_file_balanced():
    """createReactNoop.js should have balanced braces after the fix."""
    source = Path(
        f"{REPO}/packages/react-noop-renderer/src/createReactNoop.js"
    ).read_text()
    open_braces = source.count("{")
    close_braces = source.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open vs {close_braces} close"
    )
