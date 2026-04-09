"""
Test outputs for OpenHands PR #13580: Status display fix.

Tests that the frontend correctly displays "Starting" when the server
reports STARTING during conversation resume, even when the WebSocket
is temporarily disconnected.
"""

import subprocess
import os
import tempfile
import re

REPO = "/workspace/OpenHands"
FRONTEND = os.path.join(REPO, "frontend")
STATUS_TS = os.path.join(FRONTEND, "src", "utils", "status.ts")
TEST_TS = os.path.join(FRONTEND, "__tests__", "utils", "status.test.ts")


def get_status_code_function(content):
    """Extract the getStatusCode function from the file content."""
    # Find the start of getStatusCode function
    match = re.search(r'export function getStatusCode\(', content)
    if not match:
        return None
    start = match.start()

    # Find the end by looking for the next export function or end of file
    # This is a simple extraction - find the closing brace at function level
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

    This was the original bug - during resume, the WebSocket disconnects temporarily
    but the server reports STARTING. The fix ensures STARTING takes priority.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()

    # Extract only the getStatusCode function
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"

    # Look for the STARTING check and DISCONNECTED check in getStatusCode only
    starting_check_found = 'conversationStatus === "STARTING"' in status_code_func
    disconnected_line_idx = status_code_func.find('webSocketStatus === "DISCONNECTED"')

    if not starting_check_found:
        assert False, "conversationStatus === 'STARTING' check not found in getStatusCode"

    if disconnected_line_idx == -1:
        assert False, "WebSocket DISCONNECTED check not found in getStatusCode"

    # Check that STARTING check comes before DISCONNECTED check
    starting_line_idx = status_code_func.find('conversationStatus === "STARTING"')

    assert starting_line_idx < disconnected_line_idx, \
        f"STARTING check should come before DISCONNECTED check in getStatusCode. " \
        f"STARTING at offset {starting_line_idx}, DISCONNECTED at offset {disconnected_line_idx}"


def test_conversation_starting_priority_with_connected_websocket():
    """
    FAIL-TO-PASS: When conversation status is STARTING with CONNECTED WebSocket and null agent state,
    should return COMMON$STARTING, not runtime status.

    This tests that STARTING takes priority over runtime status checks.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()

    # Extract only the getStatusCode function
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"

    # Check if the fix is present
    if 'conversationStatus === "STARTING"' not in status_code_func:
        assert False, "conversationStatus === 'STARTING' check not found in getStatusCode"

    # The fix should be placed after STOPPED check but before agent state/runtime checks
    stopped_idx = status_code_func.find('conversationStatus === "STOPPED"')
    starting_idx = status_code_func.find('conversationStatus === "STARTING"')
    agent_is_ready_idx = status_code_func.find('const agentIsReady')

    assert starting_idx != -1, "STARTING check not found in getStatusCode"

    # STARTING check should be after STOPPED check (if STOPPED exists in getStatusCode)
    if stopped_idx != -1:
        assert starting_idx > stopped_idx, \
            "STARTING check should come after STOPPED check in getStatusCode"

    # STARTING check should be before agent state checks (runtime status logic)
    if agent_is_ready_idx != -1:
        assert starting_idx < agent_is_ready_idx, \
            "STARTING check should come before agent state/runtime checks in getStatusCode"


def test_status_utility_file_exists():
    """
    PASS-TO-PASS: The status.ts utility file should exist.
    """
    assert os.path.exists(STATUS_TS), f"status.ts file not found at {STATUS_TS}"


def test_test_file_exists():
    """
    PASS-TO-PASS: The status.test.ts test file should exist.
    """
    assert os.path.exists(TEST_TS), f"status.test.ts file not found at {TEST_TS}"


def test_conversation_starting_check_in_code():
    """
    FAIL-TO-PASS: The fix should include the conversationStatus === "STARTING" check in getStatusCode.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()

    # Extract only the getStatusCode function
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"

    # Check for the new priority check added in the fix
    assert 'conversationStatus === "STARTING"' in status_code_func, \
        "Missing the conversationStatus === 'STARTING' check in getStatusCode function"


def test_priority_comment_in_code():
    """
    FAIL-TO-PASS: The fix should include the explanatory comment about priority in getStatusCode.
    """
    with open(STATUS_TS, 'r') as f:
        content = f.read()

    # Extract only the getStatusCode function
    status_code_func = get_status_code_function(content)
    if status_code_func is None:
        assert False, "Could not find getStatusCode function"

    # Check for the distinctive comment from the fix
    assert "PRIORITY 2.5: Handle conversation starting state" in status_code_func, \
        "Missing the PRIORITY 2.5 comment in getStatusCode function"


def test_status_test_file_passes():
    """
    PASS-TO-PASS: All status utility tests should pass (repo's own test suite).
    """
    result = subprocess.run(
        ["npm", "test", "--", "status.test.ts", "--no-coverage"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Status tests failed:\n{result.stdout}\n{result.stderr}"


def test_new_test_case_added():
    """
    FAIL-TO-PASS: The test file should include the new test case for STARTING with disconnected websocket.
    """
    with open(TEST_TS, 'r') as f:
        content = f.read()

    # Check for the new test case name
    assert "show Starting when conversation status is STARTING even with disconnected websocket" in content, \
        "Missing the new test case for STARTING with disconnected websocket"


# =============================================================================
# Pass-to-pass tests for repo CI/CD gates
# These ensure the fix doesn't break existing functionality
# =============================================================================


def test_repo_typecheck():
    """
    PASS-TO-PASS: Repo TypeScript typecheck passes.
    Ensures the fix doesn't introduce type errors.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_repo_build():
    """
    PASS-TO-PASS: Repo frontend build passes.
    Ensures the fix doesn't break the production build.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout}\n{result.stderr}"


def test_repo_lint():
    """
    PASS-TO-PASS: Repo lint checks pass.
    Ensures the fix follows code style and quality standards.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_status_tests():
    """
    PASS-TO-PASS: Status utility-specific tests pass.
    Ensures the fix doesn't break existing status utility tests.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "status.test.ts", "--no-coverage"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Status tests failed:\n{result.stdout}\n{result.stderr}"
