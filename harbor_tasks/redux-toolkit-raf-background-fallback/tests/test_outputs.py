#!/usr/bin/env python3
"""
Test suite for redux-toolkit PR #5273:
Add setTimeout fallback to raf autoBatch strategy for background tabs.

This tests that the autoBatchEnhancer with 'raf' type properly falls back
to setTimeout when requestAnimationFrame is stalled (as in background tabs).
"""

import subprocess
import sys
import os

# Path to the repo inside the Docker container
REPO = "/workspace/redux-toolkit/packages/toolkit"


def test_raf_fallback_function_exists():
    """
    Fail-to-pass: The createRafWithFallbackTimer helper function must exist
    and be properly structured to race RAF against setTimeout.
    """
    target_file = os.path.join(REPO, "src/autoBatchEnhancer.ts")
    with open(target_file, 'r') as f:
        content = f.read()

    # Check that the helper function exists
    assert "createRafWithFallbackTimer" in content, \
        "createRafWithFallbackTimer helper function not found"

    # Check that it uses both RAF and setTimeout
    assert "requestAnimationFrame" in content and "setTimeout" in content, \
        "Function must use both RAF and setTimeout"

    # Check that it handles the race condition with a 'called' flag
    assert "called" in content, \
        "Must track 'called' flag to prevent double notification"

    # Check that it cancels both timers when one fires
    assert "cancelAnimationFrame" in content and "clearTimeout" in content, \
        "Must cancel the other timer when one fires"


def test_raf_strategy_uses_fallback():
    """
    Fail-to-pass: The 'raf' autoBatch strategy must use createRafWithFallbackTimer
    instead of raw window.requestAnimationFrame.
    """
    target_file = os.path.join(REPO, "src/autoBatchEnhancer.ts")
    with open(target_file, 'r') as f:
        content = f.read()

    # Find the raf strategy section
    # After the fix, it should use createRafWithFallbackTimer
    raf_section_start = content.find("options.type === 'raf'")
    assert raf_section_start != -1, "RAF strategy section not found"

    # Look at the relevant section after the fix
    raf_section = content[raf_section_start:raf_section_start + 800]

    # The fix wraps RAF in createRafWithFallbackTimer with 100ms timeout
    assert "createRafWithFallbackTimer(window.requestAnimationFrame, 100)" in raf_section, \
        "RAF strategy must use createRafWithFallbackTimer with 100ms timeout"


def test_100ms_timeout_value():
    """
    Fail-to-pass: The setTimeout fallback must use exactly 100ms timeout
    to balance responsiveness with performance.
    """
    target_file = os.path.join(REPO, "src/autoBatchEnhancer.ts")
    with open(target_file, 'r') as f:
        content = f.read()

    # Check for the 100ms value specifically
    # It should appear in the createRafWithFallbackTimer call
    assert "createRafWithFallbackTimer(window.requestAnimationFrame, 100)" in content, \
        "Timeout must be exactly 100ms"


def test_unit_tests_pass():
    """
    Pass-to-pass: The existing unit tests must continue to pass.
    This validates that the fix doesn't break existing functionality.
    Origin: repo_tests
    """
    result = subprocess.run(
        ["yarn", "test", "src/tests/autoBatchEnhancer.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_full_test_suite():
    """
    Pass-to-pass: Full test suite must pass.
    This ensures the fix doesn't break any other functionality in the repo.
    Origin: repo_tests
    """
    result = subprocess.run(
        ["yarn", "test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Full test suite failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript must compile without errors.
    Origin: repo_tests
    """
    result = subprocess.run(
        ["yarn", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stderr[-500:]}"


def test_type_tests():
    """
    Pass-to-pass: TypeScript type tests must pass.
    Validates type-level correctness for the modified code.
    Origin: repo_tests
    """
    result = subprocess.run(
        ["yarn", "type-tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Type tests failed:\n{result.stderr[-500:]}"
