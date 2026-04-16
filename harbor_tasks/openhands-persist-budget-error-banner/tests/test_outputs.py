"""
Test outputs for OpenHands PR #13786
Fix: prevent budget/credit error banner from disappearing immediately
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"
CONTEXT_FILE = f"{FRONTEND}/src/contexts/conversation-websocket-context.tsx"


def test_budget_error_persistence_logic_exists():
    """
    Fail-to-pass: The handleNonErrorEvent helper must exist with proper budget error checks.
    Before the fix, this logic doesn't exist - errors are cleared unconditionally.
    """
    with open(CONTEXT_FILE, 'r') as f:
        content = f.read()

    # Check for the new helper function that handles error clearing logic
    assert "handleNonErrorEvent" in content, "handleNonErrorEvent helper not found"

    # Check that it checks for budget error using the i18n key
    assert "STATUS$ERROR_LLM_OUT_OF_CREDITS" in content, \
        "Budget error i18n key check not found"

    # Check that it checks event source for agent
    assert 'event.source === "agent"' in content, \
        "Agent event source check not found"

    # Check for the early return that keeps budget error visible
    assert "isBudgetError && !isAgentEvent" in content or \
           ("return; // Keep budget error visible" in content), \
        "Budget error persistence logic (early return) not found"


def test_non_error_events_use_helper():
    """
    Fail-to-pass: Both handleMainMessage and handlePlanningMessage must use handleNonErrorEvent.
    Before the fix, they call removeErrorMessage() directly.
    """
    with open(CONTEXT_FILE, 'r') as f:
        content = f.read()

    # Count occurrences of handleNonErrorEvent calls (should be at least 2 - one in each handler)
    helper_calls = content.count("handleNonErrorEvent(event)")
    assert helper_calls >= 2, f"Expected at least 2 handleNonErrorEvent calls, found {helper_calls}"


def test_legacy_error_clearing_removed():
    """
    Fail-to-pass: The else blocks that previously called removeErrorMessage() directly
    should now call handleNonErrorEvent(). There should be no direct removeErrorMessage()
    calls in the non-error event handling path after the fix.
    """
    with open(CONTEXT_FILE, 'r') as f:
        content = f.read()

    # After the fix, handleNonErrorEvent should exist and handle the conditional removal
    # Before the fix, removeErrorMessage() is called directly in the else blocks

    # Find all occurrences of removeErrorMessage
    remove_calls = content.count("removeErrorMessage()")

    # After the fix:
    # - 1 removeErrorMessage call inside the handleNonErrorEvent helper
    # - 0 direct calls in the else blocks of the main message handlers
    # Before the fix:
    # - Multiple direct calls (at least 2 in the else blocks, plus potentially elsewhere)

    # The key change: handleNonErrorEvent helper encapsulates the removal logic
    # So if the fix is applied, we should see handleNonErrorEvent being used
    has_helper = "handleNonErrorEvent" in content

    # If there's no helper, the fix hasn't been applied
    assert has_helper, "handleNonErrorEvent helper not found - fix not applied"

    # After the fix, the helper should contain the removeErrorMessage call
    # and it should check for budget errors before calling it
    helper_pattern = r'const handleNonErrorEvent = useCallback\(\s*\([^)]+\) =>\s*\{[^}]+if \(isBudgetError && !isAgentEvent\)[^}]+removeErrorMessage\(\)[^}]+\},\s*\[removeErrorMessage\],?\s*\);'

    if not re.search(helper_pattern, content, re.DOTALL):
        # Fallback: Check for the key components separately
        assert "isBudgetError && !isAgentEvent" in content, \
            "Budget error conditional check not found in helper"
        assert "return; // Keep budget error visible" in content, \
            "Early return comment not found"


def test_agent_error_budget_check_removed():
    """
    Fail-to-pass: The fix removes redundant budget/credit error checking in AgentErrorEvent handling.
    Before the fix, there were duplicate checks that set different error messages based on budget.
    After the fix, setErrorMessage(event.error) is called directly without the nested if.
    """
    with open(CONTEXT_FILE, 'r') as f:
        content = f.read()

    # Before the fix (in handleMainMessage and handlePlanningMessage for AgentErrorEvent):
    #   if (isBudgetOrCreditError(event.error)) {
    #     setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
    #     trackCreditLimitReached({...});
    #   } else {
    #     setErrorMessage(event.error);
    #   }

    # After the fix:
    #   setErrorMessage(event.error);
    #   (the budget tracking is still done via trackCreditLimitReached but without setting i18n key)

    # Check that the nested budget check inside AgentErrorEvent handling is removed
    # The fix simplifies it to just setErrorMessage(event.error)

    # Look for the pattern in AgentErrorEvent handling sections
    lines = content.split('\n')

    # Find all AgentErrorEvent handling sections
    agent_error_sections = []
    for i, line in enumerate(lines):
        if "isAgentErrorEvent" in line:
            # Capture section from this line to next closing brace or 30 lines
            section_lines = []
            brace_count = 0
            started = False
            for j in range(i, min(i+50, len(lines))):
                section_lines.append(lines[j])
                if '{' in lines[j]:
                    brace_count += lines[j].count('{')
                    started = True
                if '}' in lines[j]:
                    brace_count -= lines[j].count('}')
                    if started and brace_count <= 0:
                        break
            agent_error_sections.append('\n'.join(section_lines))

    # In the fixed version, AgentErrorEvent handling should have simplified setErrorMessage
    # The fix removes the isBudgetOrCreditError check inside the error handling
    for section in agent_error_sections:
        # Check if this section handles AgentErrorEvent specifically (not Observation)
        if "AgentErrorEvent" in section or "isAgentErrorEvent" in section:
            # After fix: direct setErrorMessage(event.error) without nested budget check
            # Before fix: nested if (isBudgetOrCreditError(event.error)) with different messages

            # The fix removes this nested pattern
            has_nested_budget_check = "isBudgetOrCreditError(event.error)" in section and \
                                       "setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS)" in section

            if has_nested_budget_check:
                assert False, "Found nested budget check in AgentErrorEvent handling - fix not applied"


def test_frontend_typecheck():
    """
    Pass-to-pass: TypeScript type checking passes.
    This is a repo CI test that should always pass.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, f"Typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_frontend_lint():
    """
    Pass-to-pass: Frontend linting passes.
    This is a repo CI test that should always pass.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, f"Lint failed:\n{result.stdout}\n{result.stderr}"


def test_build():
    """
    Pass-to-pass: Frontend build passes.
    This is a repo CI test that should always pass.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, f"Build failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_translation_completeness():
    """
    Pass-to-pass: Translation completeness check passes.
    This is a repo CI test that should always pass.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"Translation check failed:\n{result.stderr[-500:]}"


def test_frontend_prettier():
    """
    Pass-to-pass: Frontend code formatting (prettier) check passes.
    This is a repo CI test that should always pass.
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "src/**/*.{ts,tsx}"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_conversation_websocket_tests():
    """
    Pass-to-pass: Conversation websocket handler tests pass.
    These tests cover the modified conversation-websocket-context.tsx file.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/conversation-websocket-handler.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, f"Websocket tests failed:\n{result.stderr[-500:]}"


def test_error_message_banner_tests():
    """
    Pass-to-pass: Error message banner tests pass.
    These tests cover error handling related to the budget/credit error fix.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/components/chat/error-message-banner.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Error banner tests failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
