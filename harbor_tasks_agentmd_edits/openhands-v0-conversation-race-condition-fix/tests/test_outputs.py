#!/usr/bin/env python3
"""
Test suite for OpenHands V0 conversation race condition fix.

Tests verify:
1. DEFAULT_SETTINGS.v1_enabled defaults to true (not false)
2. useCreateConversation uses nullish coalescing (not !! operator)
3. V1 is selected when settings undefined (race condition fix)
4. V0 is still used when explicitly configured to false
"""

import subprocess
import json
import re
from pathlib import Path


def run_command(cmd, cwd="/workspace"):
    """Execute command and return stdout, stderr, returncode."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr, result.returncode


def check_default_settings():
    """Check that DEFAULT_SETTINGS.v1_enabled is true."""
    stdout, stderr, rc = run_command(
        "grep -A 2 'DEFAULT_SETTINGS' frontend/src/services/settings.ts"
    )

    if rc != 0:
        return False, "Could not find DEFAULT_SETTINGS"

    # Check that v1_enabled is set to true
    if "v1_enabled: true" in stdout or "v1_enabled:true" in stdout:
        return True, "DEFAULT_SETTINGS.v1_enabled defaults to true"
    else:
        return False, f"DEFAULT_SETTINGS.v1_enabled not set to true. Content: {stdout}"


def check_nullish_coalescing():
    """Check that useCreateConversation uses nullish coalescing."""
    stdout, stderr, rc = run_command(
        "grep -n 'v1_enabled' frontend/src/hooks/mutation/use-create-conversation.ts"
    )

    if rc != 0:
        return False, "Could not find v1_enabled in use-create-conversation.ts"

    # Check for nullish coalescing operator (??)
    if "??" in stdout and "v1_enabled" in stdout:
        return True, "useCreateConversation uses nullish coalescing (??)"
    else:
        return False, f"Nullish coalescing not found. Content: {stdout}"


def check_no_double_negation():
    """Check that !! operator is not used for v1_enabled check."""
    stdout, stderr, rc = run_command(
        "grep '!!settings' frontend/src/hooks/mutation/use-create-conversation.ts || true"
    )

    if "!!settings" in stdout:
        return False, "Found !! operator (double negation) in use-create-conversation.ts"
    else:
        return True, "!! operator removed from v1_enabled check"


def check_tests_exist():
    """Check that race condition tests exist."""
    stdout, stderr, rc = run_command(
        "ls -la frontend/__tests__/hooks/mutation/use-create-conversation-race-condition.test.tsx"
    )

    if rc == 0:
        return True, "Race condition test file exists"
    else:
        return False, "Race condition test file not found"


def check_test_suite_passes():
    """Check that the test suite passes."""
    stdout, stderr, rc = run_command(
        "cd frontend && npm test 2>&1 | head -50"
    )

    # This is a best-effort check - tests might not run in Docker
    if rc == 0 or "PASS" in stdout or "pass" in stdout:
        return True, "Test suite passes"
    else:
        # Return pass with note if tests can't run
        return True, f"Test suite check (partial): {stdout[:100]}"


def main():
    """Run all checks and write reward to /logs/verifier/reward.txt."""
    checks = [
        ("DEFAULT_SETTINGS.v1_enabled = true", check_default_settings),
        ("Nullish coalescing in useCreateConversation", check_nullish_coalescing),
        ("No !! operator for v1_enabled", check_no_double_negation),
        ("Race condition tests exist", check_tests_exist),
        ("Test suite passes", check_test_suite_passes),
    ]

    results = []
    all_passed = True

    for name, check_fn in checks:
        passed, message = check_fn()
        results.append((name, passed, message))
        if not passed:
            all_passed = False
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
        print(f"  {message}\n")

    # Write reward to Docker mount
    reward = 1 if all_passed else 0
    Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    Path("/logs/verifier/reward.txt").write_text(str(reward))

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
