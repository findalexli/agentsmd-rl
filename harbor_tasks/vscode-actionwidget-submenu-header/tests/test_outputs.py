"""
Task: vscode-actionwidget-submenu-header
Repo: microsoft/vscode @ ee6bfc559a9089feb8b73962fd4fb5a306821ef4
PR:   306327 — actionWidget: fix submenu group label rendered as item description

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
ACTION_LIST = f"{REPO}/src/vs/platform/actionWidget/browser/actionList.ts"
WORKSPACE_PICKER = f"{REPO}/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: TypeScript source files cannot be executed without a full
# Node/tsc build environment; all checks use file content inspection.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_header_item_pushed_for_labeled_group():
    """actionList.ts pushes an ActionListItemKind.Header item when a group has a label."""
    src = Path(ACTION_LIST).read_text()
    lines = src.splitlines()

    # Find an if (group.label) block that contains a submenuItems.push with Header kind
    found = False
    for i, line in enumerate(lines):
        if "if (group.label)" in line:
            # Look up to 12 lines ahead for the push with Header
            context = "\n".join(lines[i : i + 12])
            if "submenuItems.push" in context and "ActionListItemKind.Header" in context:
                found = True
                break

    assert found, (
        "Expected submenuItems.push({ kind: ActionListItemKind.Header, ... }) "
        "inside an if (group.label) block in actionList.ts"
    )


# [pr_diff] fail_to_pass
def test_description_no_longer_uses_group_label():
    """actionList.ts: action item description uses child.tooltip, not group.label for first child."""
    src = Path(ACTION_LIST).read_text()

    # Old broken pattern: description used group.label for the first child (ci === 0)
    assert "ci === 0 && group.label ? group.label" not in src, (
        "Old description logic (group.label as description for ci===0) must be removed"
    )
    # New correct pattern: description is always child.tooltip or undefined
    assert "description: child.tooltip || undefined" in src, (
        "Description must use child.tooltip || undefined (not group.label)"
    )


# [pr_diff] fail_to_pass
def test_workspace_picker_provider_label_moved_to_tooltip():
    """sessionWorkspacePicker.ts: provider.label is the first-child tooltip, not SubmenuAction label."""
    src = Path(WORKSPACE_PICKER).read_text()

    # Fix introduces ci (child index) into the .map() callback
    assert "ci === 0" in src, (
        "Fix must add ci index to the .map() callback so provider.label "
        "can be set as tooltip only for the first child"
    )

    # After fix, provider.label must NOT appear as the direct second argument to SubmenuAction
    # Pattern: new SubmenuAction(`...`, provider.label, ...
    bad_pattern = r"new SubmenuAction\([^,]+,\s*provider\.label\s*,"
    assert not re.search(bad_pattern, src, re.DOTALL), (
        "provider.label must not be used as SubmenuAction's label argument; "
        "it should be moved to the first child's tooltip"
    )

    # provider.label must still appear somewhere (moved to tooltip)
    assert "provider.label" in src, (
        "provider.label must still be referenced (as tooltip for first child)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_submenu_action_structure_preserved():
    """sessionWorkspacePicker.ts: SubmenuAction instantiation still exists with browse IDs."""
    src = Path(WORKSPACE_PICKER).read_text()
    assert "new SubmenuAction" in src, "SubmenuAction must still be used in sessionWorkspacePicker.ts"
    assert "workspacePicker.browse" in src, "workspacePicker.browse action IDs must still be present"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ ee6bfc559a9089feb8b73962fd4fb5a306821ef4
def test_tab_indentation_in_modified_file():
    """actionList.ts uses tab indentation as required by VS Code coding guidelines."""
    # AST-only because: TypeScript source, not executable Python
    src = Path(ACTION_LIST).read_text()
    indented_lines = [l for l in src.splitlines() if l and l[0] in ("\t", " ")]
    tab_lines = [l for l in indented_lines if l.startswith("\t")]
    # Tabs must be the dominant indentation style
    assert len(tab_lines) > 100, (
        f"actionList.ts must use tab indentation (found only {len(tab_lines)} tab-indented lines)"
    )
    space_only_lines = [l for l in indented_lines if l.startswith("    ") and not l.startswith("\t")]
    assert len(tab_lines) > len(space_only_lines) * 10, (
        f"Tab indentation must dominate: {len(tab_lines)} tab lines vs "
        f"{len(space_only_lines)} space-only lines"
    )
