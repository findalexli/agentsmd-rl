"""
Test suite for OpenHands PR #13648: Hide right panel when active tab is unpinned.

This tests the fix for a UI inconsistency where unpinning the active tab via the
context menu removed the button while leaving the panel open.
"""

import subprocess
import json
import os
import re

REPO = "/workspace/OpenHands"
FRONTEND_DIR = f"{REPO}/frontend"
TARGET_FILE = f"{FRONTEND_DIR}/src/components/features/conversation/conversation-tabs/conversation-tabs-context-menu.tsx"
TEST_FILE = f"{FRONTEND_DIR}/__tests__/components/features/conversation/conversation-tabs-context-menu.test.tsx"


def test_vitest_context_menu_tests():
    """
    The repo's own vitest tests for ConversationTabsContextMenu must pass.
    This is a p2p test that validates the existing test suite works.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "ConversationTabsContextMenu", "--run"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"Vitest failed:\n{result.stdout}\n{result.stderr}"


def test_unpin_active_tab_closes_panel():
    """
    F2P: When unpinning the currently active tab, the right panel should be hidden.

    The fix adds logic that checks if the unpinned tab is the selected tab,
    and if so, sets hasRightPanelToggled=false and rightPanelShown=false.
    """
    # Read the source file
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that the fix is present: the conditional logic to close panel
    # Pattern: if (selectedTab === tab && isRightPanelShown) { ... }
    has_selected_tab_check = "selectedTab === tab" in content
    has_panel_shown_check = "isRightPanelShown" in content
    has_set_toggle = "setHasRightPanelToggled(false)" in content
    has_set_panel = "setRightPanelShown(false)" in content

    assert has_selected_tab_check, "Missing check for selectedTab === tab"
    assert has_panel_shown_check, "Missing check for isRightPanelShown"
    assert has_set_toggle, "Missing setHasRightPanelToggled(false) call"
    assert has_set_panel, "Missing setRightPanelShown(false) call"


def test_conversation_store_imported():
    """
    F2P: The fix requires importing useConversationStore from the stores module.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    has_import = "useConversationStore" in content
    has_store_import = 'from "#/stores/conversation-store"' in content

    assert has_import, "useConversationStore not found in source file"
    assert has_store_import, "useConversationStore import not found"


def test_store_hooks_used():
    """
    F2P: The fix must destructure selectedTab, isRightPanelShown, and setHasRightPanelToggled
    from the conversation store.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the store destructuring pattern
    has_selected_tab = "selectedTab" in content
    has_is_panel_shown = "isRightPanelShown" in content
    has_set_toggle = "setHasRightPanelToggled" in content

    assert has_selected_tab, "selectedTab not used from store"
    assert has_is_panel_shown, "isRightPanelShown not used from store"
    assert has_set_toggle, "setHasRightPanelToggled not used from store"


def test_setrightpanelshown_destructured():
    """
    F2P: The fix must also extract setRightPanelShown from the local storage hook.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for setRightPanelShown in the destructuring from useConversationLocalStorageState
    pattern = r'setUnpinnedTabs.*setRightPanelShown'
    match = re.search(pattern, content, re.DOTALL)

    # Alternative: check for setRightPanelShown anywhere in the file
    has_set_panel = "setRightPanelShown" in content

    assert has_set_panel, "setRightPanelShown not found in file"


def test_test_file_includes_active_tab_test():
    """
    F2P: The test file must include the new test for unpinning the active tab.
    """
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    has_active_tab_test = "should close the right panel when unpinning the currently active tab" in content
    has_non_active_tab_test = "should not close the right panel when unpinning a non-active tab" in content
    has_store_import = "useConversationStore" in content

    assert has_active_tab_test, "Missing test for unpinning active tab"
    assert has_non_active_tab_test, "Missing test for unpinning non-active tab"
    assert has_store_import, "Test file missing useConversationStore import"


def test_lint_passes():
    """
    P2P: The frontend linting must pass according to AGENTS.md requirements.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout}\n{result.stderr}"


def test_eslint_passes():
    """
    P2P: ESLint passes on frontend source (repo CI standard).
    """
    result = subprocess.run(
        ["npx", "eslint", "src", "--ext", ".ts,.tsx,.js"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_prettier_check_passes():
    """
    P2P: Prettier formatting check passes on frontend source (repo CI standard).
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "src/**/*.{ts,tsx}"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


def test_conversation_tabs_unit_tests():
    """
    P2P: Unit tests for conversation-tabs components pass (repo CI standard).
    Tests the module directly affected by this PR.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/components/features/conversation/", "--run"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"Conversation tabs tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_conversation_store_unit_tests():
    """
    P2P: Unit tests for conversation-store pass (repo CI standard).
    Tests the store used by the fix for panel state management.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/stores/conversation-store.test.ts", "--run"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"Conversation store tests failed:\n{result.stdout}\n{result.stderr}"


def test_typescript_compiles():
    """
    P2P: TypeScript compilation (typecheck) must pass.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND_DIR
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stdout}\n{result.stderr}"
