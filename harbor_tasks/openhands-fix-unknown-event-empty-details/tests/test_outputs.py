"""Tests for OpenHands PR #13639 - Fix "Unknown event" shown for actions with empty details.

This test file validates the fix for a frontend bug where "Unknown event" was incorrectly
displayed in the chat UI for actions that legitimately have no expandable details
(e.g., file `view` commands).

Root cause: The `getEventContent()` function used a falsy check on the `details` return
value, so an empty string "" was treated as missing and replaced with "Unknown event".
"""

import subprocess
import sys
import re
import pytest

REPO = "/workspace/OpenHands"
FRONTEND_DIR = f"{REPO}/frontend"


def _run_vitest_test(test_name_pattern):
    """Run a specific vitest test and verify it actually ran.

    Returns (success, output) where success is True only if:
    1. The exit code is 0
    2. At least one test actually ran and passed (not just skipped)
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", test_name_pattern],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    output = result.stdout + result.stderr

    # If return code is non-zero, the test definitely failed
    if result.returncode != 0:
        return False, f"Test failed with exit code {result.returncode}:\n{output}"

    # Check that at least one test actually PASSED (not just skipped)
    # Look for patterns like "1 passed" or checkmark indicators
    # If all tests are skipped, the pattern won't match anything
    has_passed_tests = bool(
        re.search(r'(\d+) passed', output) and
        not re.search(r'(\d+) passed.*\(0\)', output)  # exclude "0 passed"
    )

    # Check for actual passing indicators (✓, ✔, or "passed" with count > 0)
    passed_indicator = bool(
        re.search(r'[✓✔]', output) or  # Unicode checkmarks
        re.search(r'Test Files.*passed', output) or
        re.search(r'Tests.*passed', output)
    )

    # If all tests were skipped, fail the test
    all_skipped = "skipped" in output.lower() and not has_passed_tests

    if all_skipped or not passed_indicator:
        return False, f"No tests matched pattern '{test_name_pattern}' - test may not exist yet:\n{output}"

    return True, output


def test_vitest_file_view_action():
    """Test that file view action returns empty details instead of 'Unknown event'.

    This is a fail-to-pass test: it validates that the fix correctly handles
    the case where a file view action (which has no expandable details) returns
    an empty string for details rather than the "Unknown event" fallback.
    """
    passed, output = _run_vitest_test("returns empty details for file view action")
    assert passed, output


def test_vitest_malformed_action_event():
    """Test that action-like events missing tool_name/tool_call_id show action kind.

    This is a fail-to-pass test: it validates that the lenient fallback branch
    correctly extracts a title from the action kind for events that have an
    action object but fail the strict isActionEvent() type guard.
    """
    passed, output = _run_vitest_test("shows action kind for action-like events")
    assert passed, output


def test_frontend_lint():
    """Frontend linting passes (pass-to-pass).

    This test runs the repo's own linting command to ensure the code passes
    the project's linting standards. This is a pass-to-pass test that
    should pass on both base and fixed commits.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-1000:]}"


def test_repo_translation_completeness():
    """Translation completeness check passes (pass-to-pass).

    This test verifies that all translation keys have complete language
    coverage. This is a repo CI check that runs in the lint workflow.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stderr[-500:]}"


def test_repo_unit_tests_event_helpers():
    """Event content helpers unit tests pass (pass-to-pass).

    This test runs the specific unit tests for event-content-helpers which
    cover related functionality to the modified get-event-content code.
    This is a curated subset of the repo's tests relevant to the PR changes.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/components/v1/chat/event-content-helpers/"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Event helpers tests failed:\n{result.stderr[-500:]}"


def test_frontend_typecheck():
    """Frontend type checking passes (pass-to-pass).

    This test runs the repo's TypeScript type checking to ensure there are
    no type errors. This is a pass-to-pass test.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-1000:]}"


def test_get_event_content_source_v1():
    """Verify the v1 get-event-content.tsx source has the fix applied.

    This is a structural test gated by behavioral tests - it verifies that
    the specific line changes are present in the source file.
    """
    # First run behavioral tests to gate this structural test
    passed, _ = _run_vitest_test("returns empty details for file view action")
    if not passed:
        pytest.skip("Behavioral test failed - skipping structural verification")

    source_file = f"{FRONTEND_DIR}/src/components/v1/chat/event-content-helpers/get-event-content.tsx"
    with open(source_file, "r") as f:
        content = f.read()

    # Check that the fix is present: returns details without fallback
    assert "details," in content, "Expected 'details,' (without fallback) not found in v1 source"

    # Check that the lenient fallback branch is present
    assert "Lenient fallback for action-like events" in content, "Expected lenient fallback comment not found"


def test_get_event_content_source_features():
    """Verify the features get-event-content.tsx source has the fix applied.

    This is a structural test gated by behavioral tests.
    """
    # First run behavioral tests to gate this structural test
    passed, _ = _run_vitest_test("returns empty details for file view action")
    if not passed:
        pytest.skip("Behavioral test failed - skipping structural verification")

    source_file = f"{FRONTEND_DIR}/src/components/features/chat/event-content-helpers/get-event-content.tsx"
    with open(source_file, "r") as f:
        content = f.read()

    # Check that the fix is present: returns details without fallback
    assert "details," in content, "Expected 'details,' (without fallback) not found in features source"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
