"""
Tests for PR #10682: fix dropdownMenu item badge position

This PR moves the badge from being a child element to a dedicated `badge` prop
that is rendered in a specific position within the dropdown menu item.
"""

import subprocess
import re

REPO = "/workspace/excalidraw"

# File paths
DROPDOWN_MENU_ITEM = f"{REPO}/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx"
DROPDOWN_MENU_ITEM_CONTENT = f"{REPO}/packages/excalidraw/components/dropdownMenu/DropdownMenuItemContent.tsx"
ACTIONS_FILE = f"{REPO}/packages/excalidraw/components/Actions.tsx"
FONT_PICKER_LIST = f"{REPO}/packages/excalidraw/components/FontPicker/FontPickerList.tsx"
TTD_DIALOG_TRIGGER = f"{REPO}/packages/excalidraw/components/TTDDialog/TTDDialogTrigger.tsx"


def test_typescript_typecheck():
    """TypeScript type checking passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"TypeScript type checking failed:\n{result.stderr[-1000:]}"


def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"ESLint check failed:\n{result.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_repo_dropdown_unit():
    """Dropdown menu unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "test:app", "packages/excalidraw/components/dropdownMenu/DropdownMenu.test.tsx", "--watch=false"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Dropdown menu unit tests failed:\n{result.stderr[-500:]}"


def test_dropdown_menu_item_has_badge_prop():
    """DropdownMenuItem component accepts a badge prop (fail_to_pass)."""
    with open(DROPDOWN_MENU_ITEM, 'r') as f:
        content = f.read()

    # Check that badge is in the destructured props
    assert "badge," in content, "DropdownMenuItem should destructure badge prop"

    # Check that badge is in the type definition
    assert "badge?: React.ReactNode;" in content, "DropdownMenuItem type should include badge prop"

    # Check that badge is passed to MenuItemContent
    assert "badge={badge}" in content, "DropdownMenuItem should pass badge to MenuItemContent"


def test_menu_item_content_has_badge_prop():
    """MenuItemContent component accepts and renders badge prop (fail_to_pass)."""
    with open(DROPDOWN_MENU_ITEM_CONTENT, 'r') as f:
        content = f.read()

    # Check that badge is in the destructured props
    assert "badge," in content, "MenuItemContent should destructure badge prop"

    # Check that badge is in the type definition
    assert "badge?: React.ReactNode;" in content, "MenuItemContent type should include badge prop"

    # Check that badge is rendered in the correct location with the correct class
    assert '{badge && <div className="dropdown-menu-item__badge">{badge}</div>}' in content, \
        "MenuItemContent should render badge in a div with class dropdown-menu-item__badge"


def test_actions_uses_badge_prop():
    """Actions.tsx uses badge prop instead of child element (fail_to_pass)."""
    with open(ACTIONS_FILE, 'r') as f:
        content = f.read()

    # Check that badge is passed as a prop (before the children)
    assert 'badge={<DropdownMenu.Item.Badge>AI</DropdownMenu.Item.Badge>}' in content, \
        "Actions.tsx should pass badge as a prop to DropdownMenu.Item"

    # Check that badge is NOT rendered as a child (after the text)
    # The old pattern would have the badge as a child of the DropdownMenu.Item
    lines = content.split('\n')
    magicframe_item_idx = None
    for i, line in enumerate(lines):
        if 'toolbar-magicframe' in line:
            magicframe_item_idx = i
            break

    if magicframe_item_idx is not None:
        # Look at the next few lines - badge should not appear after {t("toolBar.magicframe")}
        item_content = '\n'.join(lines[magicframe_item_idx:magicframe_item_idx+10])
        # Badge should NOT be inside the children (after the text content line)
        badge_inside_children = re.search(
            r'{t\("toolBar\.magicframe"\)}\s*\n.*<DropdownMenu\.Item\.Badge>',
            item_content
        )
        assert not badge_inside_children, \
            "Badge should not be rendered as a child element inside DropdownMenu.Item"


def test_font_picker_list_uses_badge_prop():
    """FontPickerList.tsx uses badge prop instead of child element (fail_to_pass)."""
    with open(FONT_PICKER_LIST, 'r') as f:
        content = f.read()

    # Check that badge is passed as a prop
    assert 'badge={' in content and 'font.badge &&' in content, \
        "FontPickerList should pass badge as a prop with conditional rendering"

    # Check that the badge is rendered via prop, not as child after {font.text}
    # The badge JSX should appear before {font.text} (as part of the badge prop)
    lines = content.split('\n')
    font_text_idx = None
    for i, line in enumerate(lines):
        if '{font.text}' in line:
            font_text_idx = i
            break

    if font_text_idx is not None:
        # Check that DropDownMenuItemBadge does NOT appear after {font.text}
        after_font_text = '\n'.join(lines[font_text_idx:font_text_idx+5])
        assert '<DropDownMenuItemBadge' not in after_font_text, \
            "DropDownMenuItemBadge should not appear after {font.text} as a child"


def test_ttd_dialog_trigger_uses_badge_prop():
    """TTDDialogTrigger.tsx uses badge prop instead of child element (fail_to_pass)."""
    with open(TTD_DIALOG_TRIGGER, 'r') as f:
        content = f.read()

    # Check that badge is passed as a prop (before the children)
    assert 'badge={<DropdownMenu.Item.Badge>AI</DropdownMenu.Item.Badge>}' in content, \
        "TTDDialogTrigger should pass badge as a prop to DropdownMenu.Item"

    # Check that badge is NOT rendered as a child after the text content
    lines = content.split('\n')
    children_idx = None
    for i, line in enumerate(lines):
        if '{children ?? t("labels.textToDiagram")}' in line:
            children_idx = i
            break

    if children_idx is not None:
        # Check that DropdownMenu.Item.Badge does NOT appear after the text
        after_text = '\n'.join(lines[children_idx:children_idx+5])
        assert '<DropdownMenu.Item.Badge' not in after_text, \
            "Badge should not be rendered as a child element after the text content"


def test_badge_rendered_in_correct_position():
    """Badge is rendered after text content but before shortcut (fail_to_pass)."""
    with open(DROPDOWN_MENU_ITEM_CONTENT, 'r') as f:
        content = f.read()

    # The badge should be rendered after the text div and before the shortcut div
    # Looking for the pattern: text div -> badge div -> shortcut div
    pattern = r'''<div style={textStyle} className="dropdown-menu-item__text">
        <Ellipsify>{children}</Ellipsify>
      </div>
      \{badge && <div className="dropdown-menu-item__badge">\{badge\}</div>\}
      \{shortcut &&'''

    match = re.search(pattern, content)
    assert match, \
        "Badge should be rendered after the text content div and before the shortcut conditional"
