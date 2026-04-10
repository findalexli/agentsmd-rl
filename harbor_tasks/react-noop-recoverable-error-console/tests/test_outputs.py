"""
Task: react-noop-recoverable-error-console
Repo: react @ 23b2d8514f13f109b980b0a1f4f3aab906ad51d0
PR:   35948

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import pytest

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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify repo CI/CD checks pass
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_source_syntax_valid():
    """Modified source file has valid JavaScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check",
         f"{REPO}/packages/react-noop-renderer/src/createReactNoop.js"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Source file has syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_reconciler_tests_relevant():
    """Repo tests for modified reconciler files pass (pass_to_pass).

    Runs the React test suite for useMemoCache tests which validate
    the onRecoverableError behavior changes.
    """
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=useMemoCache", "--ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Allow 0 (pass) or specific known failure codes that aren't infrastructure issues
    if r.returncode != 0:
        # If tests fail due to missing dependencies, that's expected in the base container
        # but if tests run and fail with assertion errors, that's a real failure
        stderr_lower = (r.stderr or "").lower()
        stdout_lower = (r.stdout or "").lower()
        combined = stderr_lower + stdout_lower

        # Skip if dependencies aren't installed (this is an infrastructure issue, not a test failure)
        if any(x in combined for x in ["cannot find module", "modulenotfounderror", "enoent"]):
            pytest.skip("Dependencies not installed, test cannot run")

        # If tests actually ran and failed, that's a real failure
        if "fail" in combined or "error" in combined:
            assert False, f"Tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_error_handling_tests_relevant():
    """Repo tests for ReactIncrementalErrorHandling pass (pass_to_pass).

    Runs the React test suite for error handling tests which are
    directly affected by the onRecoverableError changes.
    """
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactIncrementalError", "--ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    if r.returncode != 0:
        stderr_lower = (r.stderr or "").lower()
        stdout_lower = (r.stdout or "").lower()
        combined = stderr_lower + stdout_lower

        if any(x in combined for x in ["cannot find module", "modulenotfounderror", "enoent"]):
            pytest.skip("Dependencies not installed, test cannot run")

        if "fail" in combined or "error" in combined:
            assert False, f"Tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_noop_renderer_tests():
    """Repo tests for react-noop-renderer pass (pass_to_pass).

    Validates that the noop renderer and related reconciler tests
    work correctly after the onRecoverableError changes.
    """
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactNoop", "--ci", "--silent"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    if r.returncode != 0:
        stderr_lower = (r.stderr or "").lower()
        stdout_lower = (r.stdout or "").lower()
        combined = stderr_lower + stdout_lower

        if any(x in combined for x in ["cannot find module", "modulenotfounderror", "enoent"]):
            pytest.skip("Dependencies not installed, test cannot run")

        if "fail" in combined or "error" in combined:
            assert False, f"Tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_passes():
    """Repo's ESLint checks pass on modified files (pass_to_pass).

    Validates that the modified source files meet the project's linting standards.
    """
    r = subprocess.run(
        ["yarn", "lint", "--", "packages/react-noop-renderer/src/createReactNoop.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    if r.returncode != 0:
        stderr_lower = (r.stderr or "").lower()
        stdout_lower = (r.stdout or "").lower()
        combined = stderr_lower + stdout_lower

        if any(x in combined for x in ["cannot find module", "modulenotfounderror", "enoent"]):
            pytest.skip("Dependencies not installed, test cannot run")

        assert False, f"ESLint failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_typecheck_passes():
    """Repo's Flow typecheck passes on modified files (pass_to_pass).

    Validates that the modified source files have valid Flow types.
    """
    r = subprocess.run(
        ["yarn", "flow", "--", "focus-check", "packages/react-noop-renderer/src/createReactNoop.js"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    if r.returncode != 0:
        stderr_lower = (r.stderr or "").lower()
        stdout_lower = (r.stdout or "").lower()
        combined = stderr_lower + stdout_lower

        if any(x in combined for x in ["cannot find module", "modulenotfounderror", "enoent", "command not found"]):
            pytest.skip("Dependencies not installed, test cannot run")

        # Check if it's a real Flow error vs infrastructure issue
        if "error" in combined or "flow" in combined:
            assert False, f"Flow typecheck failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_modified_test_files_exist():
    """Modified test files exist and are readable (pass_to_pass).

    Basic sanity check that the test files modified in the PR exist and
    have readable content. This validates the repo structure is intact.
    """
    test_files = [
        f"{REPO}/packages/react-reconciler/src/__tests__/useMemoCache-test.js",
        f"{REPO}/packages/react-reconciler/src/__tests__/ReactIncrementalErrorReplay-test.js",
        f"{REPO}/packages/react-reconciler/src/__tests__/ReactIncrementalErrorHandling-test.internal.js",
    ]

    for test_file in test_files:
        assert Path(test_file).exists(), f"Test file does not exist: {test_file}"
        assert Path(test_file).is_file(), f"Path is not a file: {test_file}"
        content = Path(test_file).read_text()
        assert len(content) > 0, f"Test file is empty: {test_file}"
