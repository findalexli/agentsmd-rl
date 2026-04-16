"""Tests for excalidraw preferences menu feature."""

import subprocess
import os
import json

REPO = "/workspace/excalidraw"
PACKAGES = f"{REPO}/packages/excalidraw"


def test_typescript_typecheck():
    """TypeScript type checking passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"TypeScript type check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_eslint():
    """ESLint passes with no warnings (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"ESLint check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_prettier():
    """Prettier formatting check passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_dropdownmenu_unit_tests():
    """DropdownMenu component unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/components/dropdownMenu/DropdownMenu.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"DropdownMenu unit tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_shortcuts_unit_tests():
    """Shortcuts unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/tests/shortcuts.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Shortcuts unit tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_default_sidebar_unit_tests():
    """DefaultSidebar component unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/components/DefaultSidebar.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"DefaultSidebar unit tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_toollock_shortcut_exists():
    """toolLock shortcut is added to shortcutMap (fail_to_pass)."""
    shortcuts_file = f"{PACKAGES}/actions/shortcuts.ts"
    with open(shortcuts_file, 'r') as f:
        content = f.read()

    # Check toolLock is in the ShortcutName union type
    assert '"toolLock"' in content, "toolLock not found in ShortcutName type"

    # Check toolLock is in shortcutMap
    assert "toolLock:" in content, "toolLock not found in shortcutMap"

    # Check it has the Q key shortcut
    assert 'getShortcutKey("Q")' in content, "Q key shortcut not found for toolLock"


def test_settings_icon_exists():
    """settingsIcon is exported from icons.tsx (fail_to_pass)."""
    icons_file = f"{PACKAGES}/components/icons.tsx"
    with open(icons_file, 'r') as f:
        content = f.read()

    # Check settingsIcon export exists
    assert "export const settingsIcon" in content, "settingsIcon export not found"

    # Check it contains the icon paths (distinctive part of the icon)
    assert "adjustments-horizontal" in content or "M14 6m-2" in content, "settingsIcon content not found"


def test_dropdown_menu_item_checkbox_exists():
    """DropdownMenuItemCheckbox component exists (fail_to_pass)."""
    checkbox_file = f"{PACKAGES}/components/dropdownMenu/DropdownMenuItemCheckbox.tsx"

    # File should exist
    assert os.path.exists(checkbox_file), f"DropdownMenuItemCheckbox.tsx file not found at {checkbox_file}"

    with open(checkbox_file, 'r') as f:
        content = f.read()

    # Check component definition
    assert "const DropdownMenuItemCheckbox" in content, "DropdownMenuItemCheckbox component not found"

    # Check it uses checkIcon and emptyIcon
    assert "checkIcon" in content, "checkIcon not used in DropdownMenuItemCheckbox"
    assert "emptyIcon" in content, "emptyIcon not used in DropdownMenuItemCheckbox"

    # Check it accepts checked prop
    assert "checked:" in content or "checked?" in content, "checked prop not found"


def test_dropdown_menu_exports_checkbox():
    """DropdownMenu exports ItemCheckbox (fail_to_pass)."""
    dropdown_file = f"{PACKAGES}/components/dropdownMenu/DropdownMenu.tsx"
    with open(dropdown_file, 'r') as f:
        content = f.read()

    # Check import exists
    assert "DropdownMenuItemCheckbox" in content, "DropdownMenuItemCheckbox not imported"

    # Check it is attached to DropdownMenu
    assert "DropdownMenu.ItemCheckbox = DropdownMenuItemCheckbox" in content, "DropdownMenu.ItemCheckbox assignment not found"


def test_preferences_component_exists():
    """Preferences component exists with all sub-components (fail_to_pass)."""
    default_items_file = f"{PACKAGES}/components/main-menu/DefaultItems.tsx"
    with open(default_items_file, 'r') as f:
        content = f.read()

    # Check Preferences component is exported
    assert "export const Preferences" in content, "Preferences component export not found"

    # Check it uses settingsIcon
    assert "settingsIcon" in content, "settingsIcon not used in Preferences"

    # Check it uses DropdownMenuSub
    assert "DropdownMenuSub" in content, "DropdownMenuSub not used in Preferences"

    # Check sub-components are attached
    subcomponents = [
        "Preferences.ToggleToolLock",
        "Preferences.ToggleSnapMode",
        "Preferences.ToggleGridMode",
        "Preferences.ToggleZenMode",
        "Preferences.ToggleViewMode",
        "Preferences.ToggleElementProperties",
    ]
    for subcomp in subcomponents:
        assert subcomp in content, f"{subcomp} not found in Preferences component"


def test_preferences_uses_checkbox_items():
    """Preferences uses DropdownMenuItemCheckbox for items (fail_to_pass)."""
    default_items_file = f"{PACKAGES}/components/main-menu/DefaultItems.tsx"
    with open(default_items_file, 'r') as f:
        content = f.read()

    # Check DropdownMenuItemCheckbox import
    assert "DropdownMenuItemCheckbox" in content, "DropdownMenuItemCheckbox not imported in DefaultItems"

    # Check usage in preference items
    assert "<DropdownMenuItemCheckbox" in content, "DropdownMenuItemCheckbox not used in Preferences"


def test_locale_entries_exist():
    """Locale entries for preferences exist (fail_to_pass)."""
    locale_file = f"{PACKAGES}/locales/en.json"
    with open(locale_file, 'r') as f:
        locale = json.load(f)

    labels = locale.get("labels", {})

    # Check preferences label exists
    assert "preferences" in labels, "preferences label not found in locale"
    assert labels["preferences"] == "Preferences", f"Expected 'Preferences', got '{labels.get('preferences')}'"

    # Check preferences_toolLock label exists
    assert "preferences_toolLock" in labels, "preferences_toolLock label not found in locale"
    assert labels["preferences_toolLock"] == "Tool lock", f"Expected 'Tool lock', got '{labels.get('preferences_toolLock')}'"


def test_app_main_menu_uses_preferences():
    """AppMainMenu includes Preferences item (fail_to_pass)."""
    app_menu_file = f"{REPO}/excalidraw-app/components/AppMainMenu.tsx"
    with open(app_menu_file, 'r') as f:
        content = f.read()

    # Check MainMenu.DefaultItems.Preferences is used
    assert "<MainMenu.DefaultItems.Preferences" in content, "MainMenu.DefaultItems.Preferences not used in AppMainMenu"


def test_dropdown_menu_item_props_type_exported():
    """DropdownMenuItemProps type is exported (fail_to_pass)."""
    dropdown_item_file = f"{PACKAGES}/components/dropdownMenu/DropdownMenuItem.tsx"
    with open(dropdown_item_file, 'r') as f:
        content = f.read()

    # Check type is exported
    assert "export type DropdownMenuItemProps" in content, "DropdownMenuItemProps type not exported"

    # Check it is used by DropdownMenuItem
    assert "DropdownMenuItemProps" in content, "DropdownMenuItemProps not used"


def test_shortcut_name_includes_toollock():
    """ShortcutName type includes toolLock (fail_to_pass)."""
    shortcuts_file = f"{PACKAGES}/actions/shortcuts.ts"
    with open(shortcuts_file, 'r') as f:
        content = f.read()

    # Find the ShortcutName type definition and check toolLock is there
    lines = content.split('\n')
    in_type_def = False
    type_lines = []

    for line in lines:
        if 'export type ShortcutName =' in line:
            in_type_def = True
        if in_type_def:
            type_lines.append(line)
            if line.strip().endswith(';'):
                break

    type_content = '\n'.join(type_lines)
    assert '"toolLock"' in type_content, "toolLock not found in ShortcutName type definition"


def test_required_actions_imported():
    """Required action imports added for preferences (fail_to_pass)."""
    default_items_file = f"{PACKAGES}/components/main-menu/DefaultItems.tsx"
    with open(default_items_file, 'r') as f:
        content = f.read()

    # Check required action imports
    required_actions = [
        "actionToggleGridMode",
        "actionToggleObjectsSnapMode",
        "actionToggleStats",
        "actionToggleZenMode",
        "actionToggleViewMode",
    ]

    for action in required_actions:
        assert action in content, f"{action} not imported in DefaultItems"

    # Check useApp hook is imported
    assert "useApp," in content or "useApp" in content, "useApp hook not imported"
