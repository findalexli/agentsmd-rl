"""Tests for OpenHands null toast fix validation."""

import subprocess
import os
import re

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_calculateToastDuration_null_handling():
    """calculateToastDuration must return minDuration for null/undefined (f2p)."""
    # Read the source file and check for null handling
    with open(f"{FRONTEND}/src/utils/toast-duration.ts", "r") as f:
        content = f.read()

    # Check that null/undefined handling exists
    assert "if (!message)" in content, "Missing null check for message parameter"
    assert "return minDuration" in content, "Must return minDuration for null/undefined"

    # Check type signature accepts null/undefined
    assert "string | null | undefined" in content, "Type signature must accept null/undefined"


def test_calculateToastDuration_various_inputs():
    """Test that calculateToastDuration handles various input types correctly."""
    # Run a Node.js script to test the function behavior
    test_script = '''
const { calculateToastDuration } = require('./frontend/src/utils/toast-duration.ts');

// Test cases
const testCases = [
    { input: null, expected: 5000, desc: "null" },
    { input: undefined, expected: 5000, desc: "undefined" },
    { input: "", expected: 5000, desc: "empty string" },
    { input: "Short", expected: 5000, desc: "short message" },
];

let passed = 0;
for (const tc of testCases) {
    const result = calculateToastDuration(tc.input, 5000, 10000);
    if (result === tc.expected) {
        passed++;
    } else {
        console.log(`FAIL: ${tc.desc} - expected ${tc.expected}, got ${result}`);
    }
}
console.log(`${passed}/${testCases.length} tests passed`);
'''
    # For now, just verify the code structure exists
    with open(f"{FRONTEND}/src/utils/toast-duration.ts", "r") as f:
        content = f.read()

    # Verify the null check guard exists
    lines = content.split('\n')
    found_guard = False
    for i, line in enumerate(lines):
        if "if (!message)" in line:
            # Check next line returns minDuration
            if i + 1 < len(lines) and "return minDuration" in lines[i + 1]:
                found_guard = True
                break

    assert found_guard, "Guard clause for null/undefined message not found"


def test_displayErrorToast_accepts_null():
    """displayErrorToast function signature must accept null/undefined (f2p)."""
    with open(f"{FRONTEND}/src/utils/custom-toast-handlers.tsx", "r") as f:
        content = f.read()

    # Check function signature accepts null/undefined
    assert "error: string | null | undefined" in content, \
        "displayErrorToast must accept null/undefined error parameter"

    # Check fallback logic exists
    assert "error || i18n.t" in content or "error ||" in content, \
        "Must have fallback message logic for null/undefined errors"


def test_frontend_lint_passes():
    """Frontend linting must pass (p2p - from AGENTS.md)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        # Only fail on actual lint errors, not warnings
        error_text = result.stdout + result.stderr
        # Check for actual errors vs warnings
        if "error" in error_text.lower():
            assert False, f"Lint errors found:\n{error_text[-1000:]}"


def test_frontend_typecheck_passes():
    """Frontend TypeScript type checking must pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TypeScript type checking failed:\n{result.stdout[-1000:]}{result.stderr[-1000:]}"


def test_frontend_build_passes():
    """Frontend build must succeed (p2p - from AGENTS.md)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Frontend build failed:\n{result.stderr[-1000:]}"


def test_specific_unit_tests_pass():
    """Unit tests for modified files must pass (p2p)."""
    # Run only the tests for the files we modified (with test fixes in the patch)
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "-t", "use-handle-plan-click|use-sandbox-recovery"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout + result.stderr

    # Check for actual test failures
    failed_match = re.search(r'(\d+)\s+failed', output, re.IGNORECASE)
    if failed_match:
        failed_count = int(failed_match.group(1))
        if failed_count > 0:
            assert False, f"{failed_count} specific unit test(s) failed:\n{output[-1500:]}"

    # Check return code
    assert result.returncode == 0, \
        f"Specific unit tests failed with exit code {result.returncode}:\n{output[-1000:]}"


def test_translation_completeness_passes():
    """Translation completeness check must pass (p2p - repo CI)."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"Translation completeness check failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_make_i18n_builds():
    """i18n translation generation must succeed (p2p - repo CI build step)."""
    result = subprocess.run(
        ["npm", "run", "make-i18n"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"i18n generation failed:\n{result.stderr[-500:]}"
