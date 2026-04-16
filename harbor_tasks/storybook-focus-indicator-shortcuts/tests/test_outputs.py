"""
Test outputs for storybook focus indicator shortcuts fix.

This PR fixes an issue where global keyboard shortcuts (Alt+A for addon panel,
Alt+S for sidebar) did not show the region focus indicator, while clicking
the buttons did show it.
"""

import subprocess
import sys
import os

REPO = "/workspace/storybook"
CODE_DIR = f"{REPO}/code"


def test_base_commit_checked_out():
    """Verify we're testing against the correct base commit."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Failed to get git HEAD: {result.stderr}"
    commit = result.stdout.strip()
    # Allow either base commit or any commit (for gold testing)
    assert len(commit) == 40, f"Invalid commit hash: {commit}"


def test_typescript_compiles():
    """TypeScript compilation passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "nx", "run-many", "-t", "check", "--projects=storybook,@storybook/core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"


def test_shortcuts_module_has_focus_call_for_panel():
    """
    FAIL-TO-PASS: Keyboard shortcut for addon panel (Alt+A) calls focusOnUIElement.

    The fix adds a focusOnUIElement call when wasPanelShown is false in the
    shortcuts handler for the addon panel toggle.
    """
    shortcuts_file = f"{CODE_DIR}/core/src/manager-api/modules/shortcuts.ts"

    with open(shortcuts_file, 'r') as f:
        content = f.read()

    # Check for the specific pattern: if (!wasPanelShown) { fullAPI.focusOnUIElement(...addonPanel...) }
    # This is the key fix - calling focusOnUIElement when panel wasn't shown
    pattern_found = (
        'if (!wasPanelShown)' in content and
        'focusableUIElements.addonPanel' in content and
        'forceFocus: true' in content and
        'poll: true' in content
    )

    assert pattern_found, (
        "Missing focusOnUIElement call for addon panel in shortcuts.ts. "
        "The fix should call fullAPI.focusOnUIElement(focusableUIElements.addonPanel, "
        "{ forceFocus: true, poll: true }) when !wasPanelShown."
    )


def test_shortcuts_module_has_focus_call_for_sidebar():
    """
    FAIL-TO-PASS: Keyboard shortcut for sidebar (Alt+S) calls focusOnUIElement.

    The fix adds a focusOnUIElement call when wasNavShown is false in the
    shortcuts handler for the sidebar toggle.
    """
    shortcuts_file = f"{CODE_DIR}/core/src/manager-api/modules/shortcuts.ts"

    with open(shortcuts_file, 'r') as f:
        content = f.read()

    # Check for the specific pattern: if (!wasNavShown) { fullAPI.focusOnUIElement(...sidebarRegion...) }
    pattern_found = (
        'if (!wasNavShown)' in content and
        'focusableUIElements.sidebarRegion' in content and
        'forceFocus: true' in content and
        'poll: true' in content
    )

    assert pattern_found, (
        "Missing focusOnUIElement call for sidebar in shortcuts.ts. "
        "The fix should call fullAPI.focusOnUIElement(focusableUIElements.sidebarRegion, "
        "{ forceFocus: true, poll: true }) when !wasNavShown."
    )


def test_panel_uses_focusable_ui_elements_constant():
    """
    FAIL-TO-PASS: Panel.tsx uses focusableUIElements constant instead of hardcoded string.

    The fix changes the id prop from hardcoded "storybook-panel-root" to
    focusableUIElements.storyPanelRoot constant.
    """
    panel_file = f"{CODE_DIR}/core/src/manager/components/panel/Panel.tsx"

    with open(panel_file, 'r') as f:
        content = f.read()

    # Should use the constant, not the hardcoded string
    uses_constant = 'focusableUIElements.storyPanelRoot' in content
    uses_hardcoded = 'id="storybook-panel-root"' in content

    assert uses_constant, (
        "Panel.tsx should use focusableUIElements.storyPanelRoot constant "
        "instead of hardcoded 'storybook-panel-root' string."
    )
    assert not uses_hardcoded, (
        "Panel.tsx should not have hardcoded 'id=\"storybook-panel-root\"' - "
        "use focusableUIElements.storyPanelRoot instead."
    )


def test_addons_showpanel_uses_forcefocus_param():
    """
    FAIL-TO-PASS: addons.tsx showPanel function takes forceFocus parameter.

    The fix changes the showPanel function signature from accepting an optional
    animateLandmark callback to accepting a forceFocus boolean parameter.
    """
    addons_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/addons.tsx"

    with open(addons_file, 'r') as f:
        content = f.read()

    # Check for the new signature: showPanel: async (forceFocus: boolean)
    has_new_signature = 'showPanel: async (forceFocus: boolean)' in content

    # Should NOT have the old signature with animateLandmark
    has_old_signature = 'animateLandmark?: (e: HTMLElement | null) => void' in content

    assert has_new_signature, (
        "addons.tsx showPanel function should take 'forceFocus: boolean' parameter. "
        "The fix refactors from animateLandmark callback to forceFocus boolean."
    )
    assert not has_old_signature, (
        "addons.tsx should not have old animateLandmark parameter signature."
    )


def test_menu_showsidebar_uses_forcefocus_param():
    """
    FAIL-TO-PASS: menu.tsx showSidebar function takes forceFocus parameter.

    The fix changes the showSidebar function signature from accepting an optional
    animateLandmark callback to accepting a forceFocus boolean parameter.
    """
    menu_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/menu.tsx"

    with open(menu_file, 'r') as f:
        content = f.read()

    # Check for the new signature
    has_new_signature = 'showSidebar: async (forceFocus: boolean)' in content

    # Should NOT have the old signature
    has_old_signature = 'animateLandmark?: (e: HTMLElement | null) => void' in content

    assert has_new_signature, (
        "menu.tsx showSidebar function should take 'forceFocus: boolean' parameter. "
        "The fix refactors from animateLandmark callback to forceFocus boolean."
    )
    assert not has_old_signature, (
        "menu.tsx should not have old animateLandmark parameter signature."
    )


def test_addons_click_calls_showpanel_false():
    """
    FAIL-TO-PASS: addons.tsx onClick calls showPanel(false).

    When clicking the addon panel button, focus animation should NOT be forced
    (the button click itself provides focus indication).
    """
    addons_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/addons.tsx"

    with open(addons_file, 'r') as f:
        content = f.read()

    # Check that onClick calls showPanel(false)
    onclick_pattern = 'onClick={() => showPanel(false)}' in content

    assert onclick_pattern, (
        "addons.tsx onClick should call showPanel(false). "
        "Clicking the button doesn't need forced focus since the button is already focused."
    )


def test_addons_keydown_calls_showpanel_true():
    """
    FAIL-TO-PASS: addons.tsx onKeyDown calls showPanel(true).

    When activating the addon panel button via keyboard (Enter/Space),
    focus animation SHOULD be forced since the button loses focus.
    """
    addons_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/addons.tsx"

    with open(addons_file, 'r') as f:
        content = f.read()

    # Check that onKeyDown calls showPanel(true)
    # This is inside the onKeyDown handler
    keydown_calls_true = 'showPanel(true)' in content

    assert keydown_calls_true, (
        "addons.tsx onKeyDown should call showPanel(true). "
        "Keyboard activation needs forced focus animation since button loses focus."
    )


def test_menu_click_calls_showsidebar_false():
    """
    FAIL-TO-PASS: menu.tsx onClick calls showSidebar(false).

    When clicking the sidebar button, focus animation should NOT be forced.
    """
    menu_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/menu.tsx"

    with open(menu_file, 'r') as f:
        content = f.read()

    onclick_pattern = 'onClick={() => showSidebar(false)}' in content

    assert onclick_pattern, (
        "menu.tsx onClick should call showSidebar(false). "
        "Clicking the button doesn't need forced focus."
    )


def test_menu_keydown_calls_showsidebar_true():
    """
    FAIL-TO-PASS: menu.tsx onKeyDown calls showSidebar(true).

    When activating the sidebar button via keyboard, focus SHOULD be forced.
    """
    menu_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/menu.tsx"

    with open(menu_file, 'r') as f:
        content = f.read()

    keydown_calls_true = 'showSidebar(true)' in content

    assert keydown_calls_true, (
        "menu.tsx onKeyDown should call showSidebar(true). "
        "Keyboard activation needs forced focus animation."
    )


def test_no_useRegionFocusAnimation_in_addons():
    """
    FAIL-TO-PASS: addons.tsx no longer imports or uses useRegionFocusAnimation.

    The fix removes the useRegionFocusAnimation hook since focus animation
    is now handled within the shortcut handlers.
    """
    addons_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/addons.tsx"

    with open(addons_file, 'r') as f:
        content = f.read()

    no_import = 'useRegionFocusAnimation' not in content

    assert no_import, (
        "addons.tsx should not import or use useRegionFocusAnimation. "
        "This hook is no longer needed - focus animation is handled in shortcuts.ts."
    )


def test_no_useRegionFocusAnimation_in_menu():
    """
    FAIL-TO-PASS: menu.tsx no longer imports or uses useRegionFocusAnimation.
    """
    menu_file = f"{CODE_DIR}/core/src/manager/components/preview/tools/menu.tsx"

    with open(menu_file, 'r') as f:
        content = f.read()

    no_import = 'useRegionFocusAnimation' not in content

    assert no_import, (
        "menu.tsx should not import or use useRegionFocusAnimation."
    )


def test_syntax_valid_in_modified_files():
    """
    PASS-TO-PASS: All modified TypeScript files have valid syntax.

    Parse the modified files to ensure no syntax errors were introduced.
    """
    import re

    ts_files = [
        f"{CODE_DIR}/core/src/manager-api/modules/shortcuts.ts",
        f"{CODE_DIR}/core/src/manager/components/panel/Panel.tsx",
        f"{CODE_DIR}/core/src/manager/components/preview/tools/addons.tsx",
        f"{CODE_DIR}/core/src/manager/components/preview/tools/menu.tsx",
    ]

    for filepath in ts_files:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for balanced braces as a basic syntax check
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"Unbalanced braces in {filepath}"

        # Check for balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"Unbalanced parentheses in {filepath}"

        # Check file doesn't contain obvious syntax errors like double semicolons
        assert ';;' not in content, f"Double semicolon found in {filepath}"


def test_repo_shortcut_unit_tests():
    """
    PASS-TO-PASS: Repo shortcut library unit tests pass (pass_to_pass).

    Tests the keyboard shortcut parsing and handling utilities in manager-api.
    These tests exercise the shortcut system that the fix modifies.
    """
    r = subprocess.run(
        ["yarn", "vitest", "run", "--config=code/core/vitest.config.ts",
         "code/core/src/manager-api/lib/shortcut.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Shortcut unit tests failed:\n{r.stderr[-1000:]}"


def test_repo_manager_api_status_tests():
    """
    PASS-TO-PASS: Repo manager-api status tests pass (pass_to_pass).

    Tests the status module in manager-api which is closely related to
    the UI state management system being modified.
    """
    r = subprocess.run(
        ["yarn", "vitest", "run", "--config=code/core/vitest.config.ts",
         "code/core/src/manager-api/tests/statuses.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Manager-api status tests failed:\n{r.stderr[-1000:]}"


def test_repo_manager_api_versions_tests():
    """
    PASS-TO-PASS: Repo manager-api versions tests pass (pass_to_pass).

    Tests the versions module in manager-api, part of the core manager
    API infrastructure that supports the modified components.
    """
    r = subprocess.run(
        ["yarn", "vitest", "run", "--config=code/core/vitest.config.ts",
         "code/core/src/manager-api/tests/versions.test.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Manager-api versions tests failed:\n{r.stderr[-1000:]}"


def test_repo_manager_sidebar_utils():
    """
    PASS-TO-PASS: Repo manager sidebar utils tests pass (pass_to_pass).

    Tests the FileSearchModal utilities in the sidebar component.
    The sidebar is one of the UI components affected by the focus fix.
    """
    r = subprocess.run(
        ["yarn", "vitest", "run", "--config=code/core/vitest.config.ts",
         "code/core/src/manager/components/sidebar/FileSearchModal.utils.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Manager sidebar utils tests failed:\n{r.stderr[-1000:]}"


def test_repo_manager_api_store_tests():
    """
    PASS-TO-PASS: Repo manager-api store tests pass (pass_to_pass).

    Tests the store module in manager-api which provides the state
    management foundation for the UI components being modified.
    """
    r = subprocess.run(
        ["yarn", "vitest", "run", "--config=code/core/vitest.config.ts",
         "code/core/src/manager-api/tests/store.test.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Manager-api store tests failed:\n{r.stderr[-1000:]}"


def test_repo_core_theming_tests():
    """
    PASS-TO-PASS: Repo core theming tests pass (pass_to_pass).

    Tests the theming system used by the manager UI components.
    The focus indicator animation relies on the theming system.
    """
    r = subprocess.run(
        ["yarn", "vitest", "run", "--config=code/core/vitest.config.ts",
         "code/core/src/theming/tests/create.test.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Core theming tests failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
