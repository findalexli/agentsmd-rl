#!/usr/bin/env python3
"""
Tests for OpenHands PR #13648: Fix bug where unpinning active tab didn't close panel.

This task tests:
1. The fix is applied (fail-to-pass): check for proper handling of active tab unpinning
2. Existing repo tests pass (pass-to-pass): vitest tests in the test file
3. Code quality (pass-to-pass): lint and typecheck pass
"""

import subprocess
import sys
import os
import pytest

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"
TARGET_FILE = f"{FRONTEND}/src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx"
TEST_FILE = f"{FRONTEND}/__tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx"


def test_active_tab_panel_close_fix_present():
    """
    Fail-to-pass: The fix for closing panel when unpinning active tab must be present.

    The fix adds a check in handleTabClick: when unpinning a tab, if it's the
    currently selected tab AND the right panel is shown, close the panel.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the core logic: checking if selectedTab matches the tab being unpinned
    assert "selectedTab === tab" in content, \
        "Missing check for whether unpinned tab is the active tab"

    # Check for the isRightPanelShown condition
    assert "isRightPanelShown" in content, \
        "Missing isRightPanelShown state access"

    # Check that setHasRightPanelToggled is called with false
    assert "setHasRightPanelToggled(false)" in content, \
        "Missing call to setHasRightPanelToggled(false) when closing panel"

    # Check that setRightPanelShown is called with false
    assert "setRightPanelShown(false)" in content, \
        "Missing call to setRightPanelShown(false) when closing panel"

    # Verify all three conditions are in the same conditional block (order matters)
    # Find the conditional block structure
    lines = content.split('\n')
    in_conditional = False
    found_selected_check = False
    found_set_has_toggled = False
    found_set_shown = False

    for line in lines:
        if 'selectedTab === tab && isRightPanelShown' in line:
            in_conditional = True
            found_selected_check = True
        elif in_conditional and 'setHasRightPanelToggled(false)' in line:
            found_set_has_toggled = True
        elif in_conditional and 'setRightPanelShown(false)' in line:
            found_set_shown = True

    assert found_selected_check, "selectedTab === tab check not found in conditional"
    assert found_set_has_toggled, "setHasRightPanelToggled(false) not found after check"
    assert found_set_shown, "setRightPanelShown(false) not found after check"


def test_conversation_store_imported():
    """
    Fail-to-pass: The conversation store must be imported and used.

    Without the store import, the fix cannot access selectedTab and isRightPanelShown.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the store import
    assert 'import { useConversationStore } from "#/stores/conversation-store"' in content, \
        "Missing import for useConversationStore"

    # Check that store is destructured for the needed state
    assert "selectedTab" in content, "selectedTab not accessed from conversation store"
    assert "isRightPanelShown" in content, "isRightPanelShown not accessed from conversation store"
    assert "setHasRightPanelToggled" in content, "setHasRightPanelToggled not accessed from store"


def test_setrightpanelshown_destructured():
    """
    Fail-to-pass: setRightPanelShown must be destructured from localStorage hook.

    The fix requires calling setRightPanelShown to update localStorage state.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for destructuring of setRightPanelShown from useConversationLocalStorageState
    assert "setRightPanelShown" in content, \
        "setRightPanelShown not destructured from useConversationLocalStorageState"


def test_repo_vitest_tests_pass():
    """
    Pass-to-pass: The repo's own vitest tests for this component must pass.

    This validates the fix doesn't break existing functionality and new tests pass.
    Source: .github/workflows/fe-unit-tests.yml runs vitest tests for PRs touching frontend.
    """
    # Run the specific test file for the modified component
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Repo vitest tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_lint_passes():
    """
    Pass-to-pass: Frontend linting must pass (mandatory per AGENTS.md).

    AGENTS.md requires lint to pass before pushing changes.
    Source: .github/workflows/lint.yml runs eslint and prettier on frontend.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Frontend lint failed:\n{result.stderr[-500:]}"


def test_repo_typecheck_passes():
    """
    Pass-to-pass: Frontend typecheck must pass (mandatory per AGENTS.md).

    Type errors would indicate improper TypeScript usage.
    Source: .github/workflows/lint.yml runs tsc after make-i18n.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Frontend typecheck failed:\n{result.stderr[-500:]}"


def test_repo_translation_completeness():
    """
    Pass-to-pass: Translation completeness check must pass.

    All translation keys must have complete language coverage.
    Source: .github/workflows/lint.yml runs check-translation-completeness.
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"Translation completeness check failed:\n{result.stderr[-500:]}"


def test_repo_build():
    """
    Pass-to-pass: Frontend build must succeed.

    Build errors would indicate bundling/compiling issues.
    Source: .github/workflows/fe-unit-tests.yml runs npm run build before tests.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Frontend build failed:\n{result.stderr[-500:]}"


def test_new_tests_for_active_tab_unpin():
    """
    Fail-to-pass: New tests for active tab unpin behavior must be present.

    The PR adds two new tests:
    1. should close the right panel when unpinning the currently active tab
    2. should not close the right panel when unpinning a non-active tab
    """
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Check for the first new test case
    assert "should close the right panel when unpinning the currently active tab" in content, \
        "Missing test: 'should close the right panel when unpinning the currently active tab'"

    # Check for the second new test case
    assert "should not close the right panel when unpinning a non-active tab" in content, \
        "Missing test: 'should not close the right panel when unpinning a non-active tab'"

    # Check that the tests use the store to verify behavior
    assert "useConversationStore.getState()" in content, \
        "Tests should verify store state with useConversationStore.getState()"

    # Check that tests verify hasRightPanelToggled is set to false
    assert "hasRightPanelToggled).toBe(false)" in content, \
        "Test should verify hasRightPanelToggled is false"

    # Check that tests verify localStorage rightPanelShown is set to false
    assert "rightPanelShown).toBe(false)" in content, \
        "Test should verify localStorage rightPanelShown is false"


def test_store_initialization_in_tests():
    """
    Fail-to-pass: Tests must properly initialize the conversation store.

    The tests need to set up the store state beforeEach to simulate the bug condition.
    """
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Check for useConversationStore import
    assert 'import { useConversationStore } from "#/stores/conversation-store"' in content, \
        "Missing import for useConversationStore in test file"

    # Check for store initialization in beforeEach
    assert "useConversationStore.setState" in content, \
        "Missing useConversationStore.setState in test setup"

    # Check for the specific state values being set
    assert 'selectedTab: "editor"' in content, \
        "Test should set selectedTab to 'editor' in beforeEach"
    assert "isRightPanelShown: true" in content, \
        "Test should set isRightPanelShown to true in beforeEach"
    assert "hasRightPanelToggled: true" in content, \
        "Test should set hasRightPanelToggled to true in beforeEach"
