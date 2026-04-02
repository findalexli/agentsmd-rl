"""
Task: vscode-submenu-header-label
Repo: microsoft/vscode @ 29f5047784335d81e143570a307f75f7800c603a
PR:   306327

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
ACTIONLIST = Path(f"{REPO}/src/vs/platform/actionWidget/browser/actionList.ts")
PICKER = Path(f"{REPO}/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: TypeScript UI code requires Electron/browser runtime to execute
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_header_item_emitted_for_labeled_groups():
    """actionList.ts pushes a Header item when a submenu group has a label."""
    content = ACTIONLIST.read_text()
    assert re.search(r'if\s*\(\s*group\.label\s*\)', content), \
        "Missing: if (group.label) conditional in actionList.ts"
    assert "ActionListItemKind.Header" in content, \
        "Missing: ActionListItemKind.Header in actionList.ts"


# [pr_diff] fail_to_pass
def test_description_simplified_to_child_tooltip():
    """description field no longer conditionally injects group.label; uses child.tooltip only."""
    content = ACTIONLIST.read_text()
    assert "ci === 0 && group.label" not in content, \
        "Old conditional group.label in description is still present"
    assert "description: child.tooltip || undefined" in content, \
        "New simplified description pattern is missing"


# [pr_diff] fail_to_pass
def test_session_picker_submenu_label_cleared():
    """SubmenuAction in sessionWorkspacePicker.ts uses empty string as label, not provider.label."""
    content = PICKER.read_text()
    assert "SubmenuAction(" in content, \
        "SubmenuAction call was removed from sessionWorkspacePicker.ts"
    assert not re.search(
        r'`workspacePicker\.browse\.\$\{provider\.id\}`\s*,\s*\n?\s*provider\.label',
        content, re.DOTALL
    ), "SubmenuAction still uses provider.label as its label argument"
    assert re.search(
        r'`workspacePicker\.browse\.\$\{provider\.id\}`[^,]*,\s*\n?\s*[\'"]{2}',
        content, re.DOTALL
    ), "SubmenuAction does not use empty string as label"


# [pr_diff] fail_to_pass
def test_session_picker_provider_label_in_first_child_tooltip():
    """Provider label is passed as tooltip of the first child action (ci === 0)."""
    content = PICKER.read_text()
    assert re.search(r'tooltip:\s*ci\s*===\s*0\s*\?\s*provider\.label', content), \
        "Missing: tooltip: ci === 0 ? provider.label pattern in sessionWorkspacePicker.ts"


# [pr_diff] fail_to_pass
def test_header_push_uses_group_label_variable():
    """Header item uses group.label variable for both label and group.title (not hardcoded)."""
    content = ACTIONLIST.read_text()
    assert re.search(r'label:\s*group\.label', content), \
        "Header item push is missing: label: group.label"
    assert re.search(r'title:\s*group\.label', content), \
        "Header item push is missing: group: { title: group.label }"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — coding convention checks
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:113 @ 29f5047784335d81e143570a307f75f7800c603a
def test_conditional_uses_curly_braces():
    """if (group.label) block must use curly braces per VS Code coding guidelines."""
    # AST-only because: TypeScript UI code requires Electron/browser runtime to execute
    content = ACTIONLIST.read_text()
    assert re.search(r'if\s*\(\s*group\.label\s*\)\s*\{', content), \
        "if (group.label) conditional missing required curly braces"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — indentation convention
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ 29f5047784335d81e143570a307f75f7800c603a
def test_indentation_uses_tabs():
    """actionList.ts uses tab indentation per VS Code coding guidelines (tabs, not spaces)."""
    # AST-only because: TypeScript UI code requires Electron/browser runtime to execute
    content = ACTIONLIST.read_text()
    indented = [l for l in content.splitlines() if l and l[0] in (' ', '\t')]
    assert indented, "No indented lines found in actionList.ts"
    tab_lines = sum(1 for l in indented if l.startswith('\t'))
    space_lines = sum(1 for l in indented if l.startswith('    '))
    assert tab_lines > space_lines * 5, \
        f"File uses spaces instead of tabs: {tab_lines} tab-indented vs {space_lines} space-indented lines"
