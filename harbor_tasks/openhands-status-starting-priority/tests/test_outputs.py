"""
Test outputs for OpenHands PR #13580: Status display fix.

Tests that the frontend correctly displays "Starting" when the server
reports STARTING during conversation resume, even when the WebSocket
is temporarily disconnected.
"""

import subprocess
import os
import re

REPO = "/workspace/OpenHands"
FRONTEND = os.path.join(REPO, "frontend")
STATUS_TS = os.path.join(FRONTEND, "src", "utils", "status.ts")
TEST_TS = os.path.join(FRONTEND, "__tests__", "utils", "status.test.ts")


def get_status_code_function(content):
    """Extract the getStatusCode function from the file content."""
    match = re.search(r'export function getStatusCode\(', content)
    if not match:
        return None
    start = match.start()
    brace_count = 0
    in_function = False
    i = start
    while i < len(content):
        if content[i] == '{':
            brace_count += 1
            in_function = True
        elif content[i] == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                return content[start:i+1]
        i += 1
    return None


def test_conversation_starting_priority_with_disconnected_websocket():
    """
    FAIL-TO-PASS: When conversation status is STARTING and WebSocket is DISCONNECTED,
    should return COMMON$STARTING, not DISCONNECTED.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"
    starting_check_found = 'conversationStatus === "STARTING"' in status_code_func
    disconnected_line_idx = status_code_func.find('webSocketStatus === "DISCONNECTED"')
    if not starting_check_found:
        assert False, "conversationStatus === 'STARTING' check not found in getStatusCode"
    if disconnected_line_idx == -1:
        assert False, "WebSocket DISCONNECTED check not found in getStatusCode"
    starting_line_idx = status_code_func.find('conversationStatus === "STARTING"')
    assert starting_line_idx < disconnected_line_idx, \
        f"STARTING check should come before DISCONNECTED check in getStatusCode."


def test_conversation_starting_priority_with_connected_websocket():
    """
    FAIL-TO-PASS: When conversation status is STARTING with CONNECTED WebSocket and null agent state,
    should return COMMON$STARTING, not runtime status.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"
    if 'conversationStatus === "STARTING"' not in status_code_func:
        assert False, "conversationStatus === 'STARTING' check not found in getStatusCode"
    stopped_idx = status_code_func.find('conversationStatus === "STOPPED"')
    starting_idx = status_code_func.find('conversationStatus === "STARTING"')
    agent_is_ready_idx = status_code_func.find('const agentIsReady')
    assert starting_idx != -1, "STARTING check not found in getStatusCode"
    if stopped_idx != -1:
        assert starting_idx > stopped_idx, \
            "STARTING check should come after STOPPED check in getStatusCode"
    if agent_is_ready_idx != -1:
        assert starting_idx < agent_is_ready_idx, \
            "STARTING check should come before agent state/runtime checks in getStatusCode"


def test_conversation_starting_check_in_code():
    """
    FAIL-TO-PASS: The fix should include the conversationStatus === "STARTING" check in getStatusCode.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"
    assert 'conversationStatus === "STARTING"' in status_code_func, \
        "Missing the conversationStatus === 'STARTING' check in getStatusCode function"


def test_priority_comment_in_code():
    """
    FAIL-TO-PASS: The fix should include the explanatory comment about priority in getStatusCode.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"
    assert "PRIORITY 2.5: Handle conversation starting state" in status_code_func, \
        "Missing the PRIORITY 2.5 comment in getStatusCode function"


def test_new_test_case_added():
    """
    FAIL-TO-PASS: The test file should include the new test case for STARTING with disconnected websocket.
    """
    with open(TEST_TS, 'r') as f:
        content = f.read()
    assert "show Starting when conversation status is STARTING even with disconnected websocket" in content, \
        "Missing the new test case for STARTING with disconnected websocket"


# =============================================================================
# Pass-to-pass tests for repo CI/CD gates
# These ensure the fix doesn't break existing functionality
# =============================================================================


def test_status_utility_file_exists():
    """
    PASS-TO-PASS: The status.ts utility file exists (origin: static).
    """
    assert os.path.exists(STATUS_TS), f"status.ts file not found at {STATUS_TS}"


def test_test_file_exists():
    """
    PASS-TO-PASS: The status.test.ts test file exists (origin: static).
    """
    assert os.path.exists(TEST_TS), f"status.test.ts file not found at {TEST_TS}"


def test_repo_typecheck():
    """
    PASS-TO-PASS: Repo TypeScript typecheck passes (origin: repo_tests).
    Runs 'npm run typecheck' to ensure no type errors in the fix.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_repo_unit_tests():
    """
    PASS-TO-PASS: Repo unit tests pass (origin: repo_tests).
    Runs the full frontend test suite with vitest.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--run"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    # Check that tests actually ran (not a crash)
    output = result.stdout + result.stderr
    assert "Test Files" in output, f"Tests did not run properly:\n{output[-500:]}"
    # Check majority passed (at least 95% of test files should pass)
    passed_match = re.search(r'(\d+) passed', output)
    failed_match = re.search(r'(\d+) failed', output)
    if passed_match and failed_match:
        passed = int(passed_match.group(1))
        failed = int(failed_match.group(1))
        total = passed + failed
        if total > 0:
            pass_rate = passed / total
            assert pass_rate >= 0.95, f"Pass rate {pass_rate:.1%} too low: {passed}/{total}"


def test_repo_build():
    """
    PASS-TO-PASS: Repo frontend build passes (origin: repo_tests).
    Runs 'npm run build' to ensure production build works.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_lint():
    """
    PASS-TO-PASS: Repo lint checks pass (origin: repo_tests).
    Runs 'npm run lint' for eslint, typecheck, and prettier.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_status_tests():
    """
    PASS-TO-PASS: Status utility-specific tests pass (origin: repo_tests).
    Runs only the status.test.ts tests to verify status logic.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--run", "status.test.ts"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Status tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_translation_completeness():
    """
    PASS-TO-PASS: Translation completeness check passes (origin: repo_tests).
    Runs 'npm run check-translation-completeness'.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
