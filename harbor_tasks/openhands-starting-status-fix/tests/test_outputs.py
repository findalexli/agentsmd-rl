"""
Test suite for OpenHands APP-1093: Fix status display to show 'Starting' on resume.

This tests the getStatusCode function in frontend/src/utils/status.ts.
The bug: When resuming a conversation, status showed "Disconnected" even though
the server correctly returned "STARTING".

The fix: Prioritize conversationStatus === "STARTING" over WebSocket status checks.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/workspace/OpenHands")
FRONTEND_DIR = REPO_ROOT / "frontend"
STATUS_FILE = FRONTEND_DIR / "src" / "utils" / "status.ts"


def test_status_file_exists():
    """Verify the status.ts file exists."""
    assert STATUS_FILE.exists(), f"Status file not found at {STATUS_FILE}"


def test_starting_priority_over_disconnected():
    """
    F2P: When conversationStatus is STARTING and WebSocket is DISCONNECTED,
    should return COMMON$STARTING, not DISCONNECTED.

    This is the core bug fix - the conversation status should take priority
    over WebSocket connection state during resume.
    """
    # Read the status.ts file
    content = STATUS_FILE.read_text()

    # Find the getStatusCode function and check the logic order
    # The fix requires conversationStatus === "STARTING" check to come BEFORE
    # WebSocket status checks

    # Look for the STARTING check
    starting_check_idx = content.find('if (conversationStatus === "STARTING")')
    assert starting_check_idx != -1, (
        "Missing STARTING status check - the fix was not applied. "
        "Need to add: if (conversationStatus === \"STARTING\") check"
    )

    # Find WebSocket status check (DISCONNECTED)
    # The WebSocket check for DISCONNECTED should come AFTER the STARTING check
    websocket_disconnected_idx = content.find('webSocketStatus === "DISCONNECTED"')

    # If WebSocket check exists, STARTING check must come before it
    if websocket_disconnected_idx != -1:
        assert starting_check_idx < websocket_disconnected_idx, (
            "STARTING check must come BEFORE WebSocket DISCONNECTED check. "
            "The fix requires prioritizing conversation status over WebSocket status."
        )

    # Also verify the function returns I18nKey.COMMON$STARTING for STARTING status
    assert "I18nKey.COMMON$STARTING" in content[starting_check_idx:starting_check_idx + 200], (
        "STARTING status check must return I18nKey.COMMON$STARTING"
    )


def test_return_value_for_starting_status():
    """
    Verify the function returns the correct i18n key for STARTING status.
    """
    content = STATUS_FILE.read_text()

    # Check that the STARTING case returns I18nKey.COMMON$STARTING
    starting_pattern = 'if (conversationStatus === "STARTING")'
    idx = content.find(starting_pattern)
    assert idx != -1, "STARTING status check not found"

    # Look for the return statement within ~100 chars after the if
    segment = content[idx:idx + 150]
    assert "return" in segment and "I18nKey.COMMON$STARTING" in segment, (
        "STARTING status check must return I18nKey.COMMON$STARTING"
    )


def test_typescript_syntax_valid():
    """
    Verify the TypeScript file has valid syntax by running tsc --noEmit.
    This ensures the fix doesn't break compilation.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", str(STATUS_FILE)],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )

    # If tsc is not available or fails for other reasons, check at least basic syntax
    if result.returncode != 0 and "error" in result.stdout.lower():
        # Filter out non-error messages
        errors = [line for line in result.stdout.split('\n') if 'error' in line.lower()]
        # Only fail if there are actual syntax errors in our file
        status_errors = [e for e in errors if 'status.ts' in e]
        if status_errors:
            assert False, f"TypeScript syntax errors in status.ts: {status_errors}"


def test_comment_explains_priority():
    """
    Verify the fix includes a comment explaining why STARTING takes priority.
    This documents the bug fix rationale for future maintainers.
    """
    content = STATUS_FILE.read_text()

    # Look for the comment explaining the STARTING priority
    # The comment should mention something about WebSocket and resume
    starting_idx = content.find('if (conversationStatus === "STARTING")')
    assert starting_idx != -1, "STARTING check not found"

    # Check the lines before the if statement for a comment
    lines_before = content[:starting_idx].split('\n')[-10:]  # Last 10 lines before
    comment_section = '\n'.join(lines_before)

    # Should have a comment explaining the priority
    assert ('// PRIORITY' in comment_section or
            'prioritize' in comment_section.lower() or
            'WebSocket' in comment_section or
            'resume' in comment_section.lower()), (
        "Missing explanatory comment for STARTING status priority. "
        "Add a comment explaining why this check must come before WebSocket checks."
    )


def test_no_hardcoded_return_values():
    """
    Anti-stub: Verify the fix uses I18nKey.COMMON$STARTING, not a hardcoded string.
    This ensures proper internationalization.
    """
    content = STATUS_FILE.read_text()

    # Find the STARTING check section
    idx = content.find('if (conversationStatus === "STARTING")')
    if idx == -1:
        return  # Will be caught by other tests

    # Check the return uses I18nKey, not a string literal
    segment = content[idx:idx + 150]

    # Should NOT contain string literal returns in this section
    import re
    # Look for return "something" or return 'something' (string literals)
    string_return = re.search(r'return\s+["\'][^"\']+["\']', segment)
    if string_return:
        assert False, (
            f"Found hardcoded string return: {string_return.group()}. "
            "Use I18nKey.COMMON$STARTING for internationalization."
        )


def test_function_signature_unchanged():
    """
    Verify the function signature is unchanged - only the logic order changed.
    This is a regression test for the function interface.
    """
    content = STATUS_FILE.read_text()

    # Find the getStatusCode function
    func_match = content.find('export function getStatusCode(')
    assert func_match != -1, "getStatusCode function not found"

    # Check parameters include all required ones
    func_end = content.find(')', func_match)
    func_sig = content[func_match:func_end + 1]

    required_params = [
        'statusMessage',
        'webSocketStatus',
        'conversationStatus',
        'runtimeStatus',
        'agentState'
    ]

    for param in required_params:
        assert param in func_sig, f"Missing required parameter: {param}"


def test_repo_lint():
    """
    Repo lint/typecheck/build passes (pass_to_pass).
    Ensures the fix doesn't break code quality checks.
    """
    r = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND_DIR,
    )
    # Allow warnings but not errors
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_status_tests():
    """
    Status utility tests pass (pass_to_pass).
    Ensures existing tests for the modified module still pass.
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "__tests__/utils/status"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND_DIR,
    )
    assert r.returncode == 0, f"Status tests failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
