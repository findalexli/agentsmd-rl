"""
Test suite for OpenHands budget error persistence fix.

Tests the behavior of handleNonErrorEvent helper that ensures budget/credit
error banners persist until an agent event proves the LLM is working again.

The bug: "Run out of credits" error banner was disappearing ~500ms after appearing
because every subsequent non-error WebSocket event called removeErrorMessage().

The fix: Budget/credit errors only clear when an event with source: "agent" arrives.
"""

import subprocess
import sys
import os
from pathlib import Path

# Repository path
REPO_DIR = Path("/workspace/openhands")
FRONTEND_DIR = REPO_DIR / "frontend"


def test_budget_error_persists_on_user_event():
    """
    FAIL-TO-PASS: Budget error should NOT be cleared by user events.

    Regression test for the bug where budget error banner disappeared
    immediately after appearing because user message events cleared it.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should NOT clear budget error when user event is received", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_budget_error_persists_on_state_update():
    """
    FAIL-TO-PASS: Budget error should NOT be cleared by state update events.

    ConversationStateUpdateEvent should not clear the budget error.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should NOT clear budget error when state update event is received", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_budget_error_persists_through_multiple_non_agent_events():
    """
    FAIL-TO-PASS: Budget error should persist through rapid non-agent events.

    Simulates the original bug scenario where events arrive ~500ms apart
    and each would clear the error before the user could see it.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should NOT clear budget error when multiple non-agent events arrive in succession", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_budget_error_clears_on_agent_event():
    """
    PASS-TO-PASS: Budget error SHOULD clear when agent event is received.

    When an agent event arrives (source: "agent"), it means the LLM is
    working again (credits are available), so the budget error should clear.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should clear budget error when agent event is received", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_budget_error_clears_after_sequence_with_user_then_agent():
    """
    PASS-TO-PASS: Budget error clears after user events then agent event.

    Tests the complete flow: budget error persists through user events,
    then clears when agent event arrives.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should clear budget error when agent event arrives after user events", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_non_budget_error_clears_on_user_event():
    """
    PASS-TO-PASS: Non-budget errors should still clear on user events.

    Non-budget errors continue to be cleared by any non-error event,
    preserving existing behavior for non-credit errors.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should clear non-budget errors on any non-error event", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_non_budget_error_clears_on_state_update():
    """
    PASS-TO-PASS: Non-budget errors should clear on state update.

    State updates should clear non-budget errors as before.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should clear non-budget errors on state update", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_frontend_builds():
    """
    Structural: Frontend should build without errors.

    Ensures the fix doesn't break TypeScript compilation.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_frontend_linting_passes():
    """
    Agent config check: Frontend linting should pass.

    From AGENTS.md: "If you've made changes to the frontend, you should run
    cd frontend && npm run lint:fix && npm run build"
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Linting failed:\n{result.stderr}"


def test_repo_typecheck():
    """
    PASS-TO-PASS: Repo TypeScript typecheck passes.

    Runs react-router typegen && tsc to ensure the codebase has no
    TypeScript errors. This is part of the repo's CI pipeline.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-500:]}"


def test_repo_translation_completeness():
    """
    PASS-TO-PASS: Repo translation completeness check passes.

    Runs check-translation-completeness to ensure all i18n keys have
    complete language coverage. This is part of the repo's CI pipeline.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stderr[-500:]}"


def test_repo_unit_tests():
    """
    PASS-TO-PASS: Repo unit tests pass.

    Runs the frontend unit test suite (vitest) to ensure all existing
    tests pass on the base commit. This is part of the repo's CI pipeline.
    """
    result = subprocess.run(
        ["npm", "run", "test"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"


def test_repo_error_handling_tests():
    """
    PASS-TO-PASS: Error handling & recovery tests pass.

    Runs the error handling tests from conversation-websocket-handler.test.tsx
    which cover the modified WebSocket context code. These tests verify:
    - Budget/credit error display and behavior
    - Error clearing on various event types
    - WebSocket connection error handling
    - Error recovery scenarios

    This is part of the repo's CI pipeline and specifically tests the code
    being modified by the fix.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/conversation-websocket-handler.test.tsx", "--run"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Error handling tests failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
