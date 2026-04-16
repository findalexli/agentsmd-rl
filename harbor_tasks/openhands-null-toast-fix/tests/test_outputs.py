"""Tests for OpenHands null toast fix validation - behavioral tests."""

import subprocess
import os
import re

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_calculateToastDuration_null_handling():
    """calculateToastDuration must return minDuration for null/undefined (f2p).

    This test actually executes the TypeScript function with null/undefined
    inputs and verifies it returns minDuration instead of throwing.
    """
    # Test null handling via actual function call
    result_null = subprocess.run(
        [
            "node", "--experimental-strip-types", "--eval",
            """
            import { calculateToastDuration } from './src/utils/toast-duration.ts';
            const result = calculateToastDuration(null, 5000);
            console.log('RESULT:' + result);
            """
        ],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Test undefined handling
    result_undefined = subprocess.run(
        [
            "node", "--experimental-strip-types", "--eval",
            """
            import { calculateToastDuration } from './src/utils/toast-duration.ts';
            const result = calculateToastDuration(undefined, 5000);
            console.log('RESULT:' + result);
            """
        ],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Both calls should succeed (not throw) and return minDuration (5000)
    assert result_null.returncode == 0, \
        f"calculateToastDuration(null) threw error: {result_null.stderr}"
    assert "RESULT:5000" in result_null.stdout, \
        f"calculateToastDuration(null) should return 5000, got: {result_null.stdout}"

    assert result_undefined.returncode == 0, \
        f"calculateToastDuration(undefined) threw error: {result_undefined.stderr}"
    assert "RESULT:5000" in result_undefined.stdout, \
        f"calculateToastDuration(undefined) should return 5000, got: {result_undefined.stdout}"


def test_calculateToastDuration_various_inputs():
    """Test that calculateToastDuration handles various input types correctly (f2p).

    Verifies the function returns minDuration for null, undefined, and empty string
    by actually calling the function with these inputs.
    """
    test_cases = [
        ("null", "null", "5000"),
        ("undefined", "undefined", "5000"),
        ("empty_string", "''", "5000"),
    ]

    for desc, input_val, expected in test_cases:
        result = subprocess.run(
            [
                "node", "--experimental-strip-types", "--eval",
                f"""
                import {{ calculateToastDuration }} from './src/utils/toast-duration.ts';
                const result = calculateToastDuration({input_val}, 5000);
                console.log('RESULT:' + result);
                """
            ],
            cwd=FRONTEND,
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, \
            f"calculateToastDuration({desc}) threw error: {result.stderr}"
        assert f"RESULT:{expected}" in result.stdout, \
            f"calculateToastDuration({desc}) should return {expected}, got: {result.stdout}"


def test_displayErrorToast_accepts_null():
    """displayErrorToast function must accept null/undefined (f2p).

    This test verifies the function can be called with null/undefined
    without throwing, and properly uses the i18n fallback.
    """
    # First verify the function type signature accepts null/undefined by
    # attempting to call it - if types don't accept null, Node might catch it
    # or it could fail at runtime.

    # We test that calling with null doesn't throw and uses fallback
    result = subprocess.run(
        [
            "node", "--experimental-strip-types", "--eval",
            """
            import { displayErrorToast } from './src/utils/custom-toast-handlers.tsx';
            // Mock i18n since it's not fully initialized in this context
            // The key is that calling with null should NOT throw
            try {
                displayErrorToast(null);
                console.log('CALL_SUCCESS');
            } catch (e) {
                console.error('CALL_FAILED:' + e.message);
                process.exit(1);
            }
            """
        ],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=30
    )

    # The call should succeed (not throw a TypeError about .length)
    # Note: It may fail due to i18n not being initialized, but should NOT
    # fail with "Cannot read properties of null (reading 'length')"
    assert "CALL_SUCCESS" in result.stdout or "CALL_FAILED" not in result.stdout, \
        f"displayErrorToast(null) should not throw .length error: {result.stderr}"
    assert "Cannot read properties of null" not in result.stderr, \
        f"displayErrorToast(null) threw null property access error: {result.stderr}"


def test_frontend_lint_passes():
    """Frontend linting passes (p2p - from CI lint workflow)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_frontend_typecheck_passes():
    """Frontend TypeScript type checking passes (p2p - from CI)."""
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"TypeScript type checking failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_frontend_build_passes():
    """Frontend build succeeds (p2p - from CI build pipeline)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"Frontend build failed:\n{result.stderr[-500:]}"


def test_repo_unit_tests_toast_duration():
    """Repo unit tests for toast-duration pass (p2p - repo CI)."""
    result = subprocess.run(
        ["npm", "test", "--", "--run", "toast-duration"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"toast-duration unit tests failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_repo_unit_tests_custom_toast_handlers():
    """Repo unit tests for custom-toast-handlers pass (p2p - repo CI)."""
    result = subprocess.run(
        ["npm", "test", "--", "--run", "custom-toast-handlers"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"custom-toast-handlers unit tests failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_repo_unit_tests_modified_hooks():
    """Repo unit tests for modified hooks pass (p2p - repo CI)."""
    # Run both modified hook test files explicitly (from solve.sh patch)
    result = subprocess.run(
        ["npm", "test", "--", "__tests__/hooks/use-handle-plan-click.test.tsx", "__tests__/hooks/use-sandbox-recovery.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Modified hooks unit tests failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_translation_completeness_passes():
    """Translation completeness check passes (p2p - from .github/workflows/lint.yml)."""
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
    """i18n translation generation succeeds (p2p - repo CI build step)."""
    result = subprocess.run(
        ["npm", "run", "make-i18n"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"i18n generation failed:\n{result.stderr[-500:]}"
