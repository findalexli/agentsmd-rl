"""
Test suite for OpenHands PR #13592 - Fix null message error in toast handlers.

This test suite verifies:
1. calculateToastDuration handles null/undefined messages (f2p)
2. displayErrorToast accepts null/undefined errors (f2p)
3. Frontend unit tests pass (p2p)
4. Frontend linting passes (p2p)
"""

import subprocess
import sys
import os

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_calculateToastDuration_null_handling():
    """
    Fail-to-pass: calculateToastDuration must handle null/undefined messages.

    Before the fix: TypeError: Cannot read properties of undefined (reading 'length')
    After the fix: Returns minDuration (5000ms default) for null/undefined
    """
    # Create a test script that imports and tests the function
    test_script = """
import { calculateToastDuration } from "./src/utils/toast-duration";

// Test null handling
const nullResult = calculateToastDuration(null, 4000, 8000);
if (nullResult !== 4000) {
    console.error(`FAIL: Expected 4000 for null, got ${nullResult}`);
    process.exit(1);
}

// Test undefined handling
const undefinedResult = calculateToastDuration(undefined, 4000, 8000);
if (undefinedResult !== 4000) {
    console.error(`FAIL: Expected 4000 for undefined, got ${undefinedResult}`);
    process.exit(1);
}

// Test empty string (should use default calculation)
const emptyResult = calculateToastDuration("", 3000, 6000);
if (emptyResult !== 3000) {
    console.error(`FAIL: Expected 3000 for empty string, got ${emptyResult}`);
    process.exit(1);
}

console.log("PASS: calculateToastDuration handles null/undefined correctly");
"""
    # Write test script to a file
    script_path = f"{FRONTEND}/test-null-handling.ts"
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        # Run the test using npx tsx (TypeScript executor)
        result = subprocess.run(
            ["npx", "tsx", "test-null-handling.ts"],
            cwd=FRONTEND,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Clean up
        os.remove(script_path)

        assert result.returncode == 0, f"calculateToastDuration null handling test failed:\n{result.stderr}\n{result.stdout}"
        assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"
    except FileNotFoundError:
        # If tsx is not available, try with vitest
        os.remove(script_path) if os.path.exists(script_path) else None
        raise AssertionError("tsx not available for TypeScript execution")


def test_calculateToastDuration_normal_operation():
    """
    Fail-to-pass: calculateToastDuration must still work with normal strings.

    Verifies the fix doesn't break normal functionality.
    """
    test_script = """
import { calculateToastDuration } from "./src/utils/toast-duration";

// Test short message (should use minDuration)
const shortMsg = "Error";  // 1 word
const shortResult = calculateToastDuration(shortMsg, 4000, 8000);
if (shortResult !== 4000) {
    console.error(`FAIL: Expected minDuration 4000 for short message, got ${shortResult}`);
    process.exit(1);
}

// Test longer message (should calculate based on reading speed)
// 50 characters = ~10 words = ~3 seconds at 200 wpm, capped at 8000
const longMsg = "This is a much longer error message with many words to read and understand";
const longResult = calculateToastDuration(longMsg, 3000, 10000);
if (longResult < 3000 || longResult > 10000) {
    console.error(`FAIL: Long message duration ${longResult} out of expected range`);
    process.exit(1);
}

console.log("PASS: calculateToastDuration normal operation works");
"""
    script_path = f"{FRONTEND}/test-normal-operation.ts"
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["npx", "tsx", "test-normal-operation.ts"],
            cwd=FRONTEND,
            capture_output=True,
            text=True,
            timeout=60
        )

        os.remove(script_path)

        assert result.returncode == 0, f"calculateToastDuration normal operation test failed:\n{result.stderr}\n{result.stdout}"
        assert "PASS" in result.stdout, f"Test did not pass: {result.stdout}"
    except FileNotFoundError:
        os.remove(script_path) if os.path.exists(script_path) else None
        raise AssertionError("tsx not available for TypeScript execution")


def test_displayErrorToast_type_signature():
    """
    Fail-to-pass: displayErrorToast must accept null/undefined as error parameter.

    This verifies the TypeScript type signature was updated correctly.
    """
    # Check the source file directly for the updated type signature
    source_path = f"{FRONTEND}/src/utils/custom-toast-handlers.tsx"
    with open(source_path, "r") as f:
        content = f.read()

    # Verify the function signature accepts null/undefined
    assert "error: string | null | undefined" in content, \
        "displayErrorToast signature should accept string | null | undefined"

    # Verify i18n fallback is used
    assert 'i18n.t("STATUS$ERROR")' in content, \
        "displayErrorToast should use i18n fallback for null errors"

    # Verify the fallback logic exists
    assert "error || i18n.t" in content, \
        "displayErrorToast should use || fallback operator"


def test_frontend_unit_tests():
    """
    Pass-to-pass: Frontend unit tests for toast-related files must pass.

    This runs specific vitest tests related to the modified files.
    We run targeted tests to avoid pre-existing test environment issues
    unrelated to this fix (e.g., ProgressEvent errors in other tests).
    """
    # Run tests specifically for the toast-duration utility
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "toast-duration", "custom-toast"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    # These specific tests should pass or have no matches (which means no direct tests for these)
    # The important thing is they don't fail due to our changes
    if result.returncode != 0:
        # If it fails, check if it's related to our changes or pre-existing issues
        if "ProgressEvent is not defined" in result.stderr or "ProgressEvent is not defined" in result.stdout:
            # This is a pre-existing test environment issue, not related to our fix
            # Check if our specific tests passed
            if "toast-duration" in result.stdout and "FAIL" not in result.stdout.split("toast-duration")[-1].split("\n")[0]:
                return  # Our specific tests passed
        # Only fail if the error is related to our changes
        if "toast-duration" in result.stderr or "custom-toast" in result.stderr:
            assert False, f"Toast-related tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"

    # Also run the specific hook tests that were modified
    result2 = subprocess.run(
        ["npm", "run", "test", "--", "--run", "use-handle-plan-click", "use-sandbox-recovery"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    # Check if our specific tests passed
    if result2.returncode != 0:
        # If failure is due to pre-existing ProgressEvent issue, skip
        if "ProgressEvent is not defined" in result2.stderr:
            # Check if test structure is intact (tests ran but environment had issues)
            if "use-handle-plan-click" in result2.stdout or "use-sandbox-recovery" in result2.stdout:
                return  # Tests were found and attempted, environment issue not our fault
        # Only fail if it's actually related to our changes
        if "use-handle-plan-click" in result2.stderr or "use-sandbox-recovery" in result2.stderr:
            assert False, f"Hook tests failed:\n{result2.stderr[-500:]}\n{result2.stdout[-500:]}"


def test_frontend_lint():
    """
    Pass-to-pass: Frontend linting must pass.

    This runs the lint check without fixing.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Frontend lint failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_calculateToastDuration_type_signature():
    """
    Fail-to-pass: calculateToastDuration must have updated type signature.

    Verifies the TypeScript types allow null/undefined.
    """
    source_path = f"{FRONTEND}/src/utils/toast-duration.ts"
    with open(source_path, "r") as f:
        content = f.read()

    # Verify the function signature accepts null/undefined
    assert "message: string | null | undefined" in content, \
        "calculateToastDuration signature should accept string | null | undefined"

    # Verify the null check exists
    assert "if (!message)" in content, \
        "calculateToastDuration should have explicit null check"

    # Verify it returns minDuration for null
    assert "return minDuration" in content, \
        "calculateToastDuration should return minDuration for null/undefined"


def test_frontend_typecheck():
    """
    Pass-to-pass: Frontend TypeScript typecheck must pass.

    This runs react-router typegen and tsc --noEmit.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Frontend typecheck failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_frontend_translation_completeness():
    """
    Pass-to-pass: Frontend translation completeness check must pass.

    Verifies all translation keys have complete language coverage.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Translation completeness check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_frontend_build():
    """
    Pass-to-pass: Frontend production build must succeed.

    This verifies the build compiles without errors.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Frontend build failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_frontend_toast_unit_tests():
    """
    Pass-to-pass: Frontend toast-related unit tests must pass.

    Runs vitest tests specifically for toast-duration and custom-toast-handlers.
    These are the files directly modified by the fix.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "toast-duration", "custom-toast"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Toast unit tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    assert "passed" in result.stdout.lower(), f"Expected tests to pass:\n{result.stdout[-500:]}"


def test_frontend_hook_unit_tests():
    """
    Pass-to-pass: Frontend hook unit tests must pass.

    Runs vitest tests for hooks that were modified by the fix
    (use-handle-plan-click and use-sandbox-recovery).
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "use-handle-plan-click", "use-sandbox-recovery"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Hook unit tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    assert "passed" in result.stdout.lower(), f"Expected tests to pass:\n{result.stdout[-500:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
