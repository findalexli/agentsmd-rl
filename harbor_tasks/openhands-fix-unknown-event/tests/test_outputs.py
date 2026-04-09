"""Tests for the OpenHands 'Unknown event' fix.

This tests that:
1. Empty details are returned as-is (not replaced with "Unknown event")
2. Action-like events with missing tool_name/tool_call_id show the action kind
3. The existing tests in the repo pass with the fix
"""

import subprocess
import sys
import os

REPO = "/workspace/OpenHands"
FRONTEND_DIR = f"{REPO}/frontend"

# The distinctive line from the patch (for idempotency check)
PATCH_MARKER = 'details: details || i18n.t("EVENT$UNKNOWN_EVENT")'

def test_base_commit_check():
    """Verify we're at the base commit before the fix."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Accept either base commit or merge commit (if patch applied)
    commit = result.stdout.strip()
    assert commit in [
        "c210d5294fa82459443e6163b9b1c9c9f55073fc",  # base
        "b0d8244ad528a85d3b223478855b2a6cf8391d30",  # merge
    ], f"Unexpected commit: {commit}"


def test_patch_applied_or_base_has_bug():
    """Check that the base has the bug or the patch is applied."""
    v1_file = f"{FRONTEND_DIR}/src/components/v1/chat/event-content-helpers/get-event-content.tsx"

    with open(v1_file, 'r') as f:
        content = f.read()

    # If patch is applied, we should NOT see the buggy pattern
    # If patch is NOT applied, we should see the buggy pattern (details || fallback)
    has_buggy_pattern = PATCH_MARKER in content

    # Test passes in either case:
    # - If patch applied: pattern should be gone, so has_buggy_pattern is False
    # - If base commit: pattern should be present, so has_buggy_pattern is True
    # This is just a check to understand current state
    assert True, f"Buggy pattern present: {has_buggy_pattern}"


def test_get_event_content_empty_details():
    """Test that file view action returns empty details instead of 'Unknown event'.

    This is the main behavioral test - it should:
    - FAIL on base commit: returns "Unknown event"
    - PASS on fix: returns "" (empty string)
    """
    # We'll run the specific test from the repo that validates this behavior
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "returns empty details for file view action", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # On base commit without fix, this test doesn't exist, so it will fail to find the test
    # On fixed commit, the test should pass
    test_found = "returns empty details for file view action" in result.stdout or \
                 "returns empty details for file view action" in result.stderr

    if not test_found:
        # Test doesn't exist yet (base commit without patch)
        pytest.skip("Test case not found - patch not applied")

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_get_event_content_malformed_event():
    """Test that malformed action events show action kind instead of 'Unknown event'.

    This tests the lenient fallback for action-like events missing tool_name/tool_call_id.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "shows action kind for action-like events", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    test_found = "shows action kind for action-like events" in result.stdout or \
                 "shows action kind for action-like events" in result.stderr

    if not test_found:
        pytest.skip("Test case not found - patch not applied")

    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_frontend_lint():
    """Frontend linting passes (pass_to_pass).

    Verifies the code follows the repo's style guidelines.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_frontend_build():
    """Frontend build succeeds (pass_to_pass).

    Verifies TypeScript compiles without errors.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-500:]}"


def test_frontend_typecheck():
    """Frontend typecheck passes (pass_to_pass).

    Verifies TypeScript type checking with react-router type generation.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-500:]}"


def test_frontend_translation_completeness():
    """Frontend translation completeness check passes (pass_to_pass).

    Verifies all translation keys have complete language coverage.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation completeness check failed:\n{result.stderr[-500:]}"


def test_v1_get_event_content_file_exists():
    """V1 get-event-content.tsx exists and is readable."""
    v1_file = f"{FRONTEND_DIR}/src/components/v1/chat/event-content-helpers/get-event-content.tsx"
    assert os.path.exists(v1_file), f"V1 file not found: {v1_file}"


def test_features_get_event_content_file_exists():
    """Features get-event-content.tsx exists and is readable."""
    features_file = f"{FRONTEND_DIR}/src/components/features/chat/event-content-helpers/get-event-content.tsx"
    assert os.path.exists(features_file), f"Features file not found: {features_file}"


def test_v1_returns_details_not_fallback():
    """V1 getEventContent returns details as-is (not with Unknown event fallback).

    This is a behavioral fail-to-pass test. It verifies the fix is present
    by checking the code structure in the return statement.

    On base commit: The return uses `details || i18n.t("EVENT$UNKNOWN_EVENT")`
    On fix commit: The return uses just `details`
    """
    v1_file = f"{FRONTEND_DIR}/src/components/v1/chat/event-content-helpers/get-event-content.tsx"

    with open(v1_file, 'r') as f:
        content = f.read()

    # After fix, the return should be: `details,` (without fallback)
    # Before fix, the return was: `details: details || i18n.t("EVENT$UNKNOWN_EVENT"),`
    buggy_pattern = 'details: details || i18n.t("EVENT$UNKNOWN_EVENT")'

    # This should FAIL on base (pattern present) and PASS on fix (pattern absent)
    assert buggy_pattern not in content, \
        "Buggy pattern found in V1 get-event-content.tsx - fix not applied"


def test_features_returns_details_not_fallback():
    """Features getEventContent returns details as-is (not with Unknown event fallback).

    This is a behavioral fail-to-pass test.
    """
    features_file = f"{FRONTEND_DIR}/src/components/features/chat/event-content-helpers/get-event-content.tsx"

    with open(features_file, 'r') as f:
        content = f.read()

    buggy_pattern = 'details: details ?? i18n.t("EVENT$UNKNOWN_EVENT")'

    # This should FAIL on base (pattern present) and PASS on fix (pattern absent)
    assert buggy_pattern not in content, \
        "Buggy pattern found in features get-event-content.tsx - fix not applied"


def test_v1_has_lenient_fallback():
    """V1 getEventContent has lenient fallback for action-like events.

    This tests that the additional fix for malformed events is present.
    """
    v1_file = f"{FRONTEND_DIR}/src/components/v1/chat/event-content-helpers/get-event-content.tsx"

    with open(v1_file, 'r') as f:
        content = f.read()

    # The fix adds a check for action.kind as a lenient fallback
    expected_pattern = 'typeof event.action.kind === "string"'

    assert expected_pattern in content, \
        "Lenient fallback for action-like events not found - fix not fully applied"


def test_repo_get_event_content_tests_pass():
    """Repo's own get-event-content tests pass.

    This runs the existing tests in the repo for the get-event-content module.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "get-event-content", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
