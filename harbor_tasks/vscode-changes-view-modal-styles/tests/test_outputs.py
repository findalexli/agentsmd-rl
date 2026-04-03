"""
Task: vscode-changes-view-modal-styles
Repo: microsoft/vscode @ 00356ebc69d09b93830f05eb4eabf872d425abdd
PR:   306421

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CHANGESVIEW_TS = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts")
CHANGESVIEW_CSS = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/media/changesView.css")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript must compile without errors after the fix is applied."""
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_modal_navigation_conditional_on_item_count():
    """openFileItem 6th arg must depend on items count, not be hardcoded true.

    Single-item lists should open without modal navigation;
    multi-item lists keep modal multi-file navigation enabled.
    """
    content = CHANGESVIEW_TS.read_text()

    # The call to openFileItem must NOT use hardcoded 'true' for the modal param
    assert (
        "openFileItem(e.element, items, e.sideBySide, "
        "!!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, true)"
    ) not in content, "openFileItem must not use hardcoded 'true' for modal navigation parameter"

    # Must use items.length > 1 (or equivalent length check) for the 6th arg
    # Match the openFileItem call and verify the 6th argument references items.length
    call_pattern = re.compile(
        r'openFileItem\(e\.element,\s*items,\s*e\.sideBySide,\s*'
        r'!!e\.editorOptions\?\.preserveFocus,\s*'
        r'!!e\.editorOptions\?\.pinned,\s*'
        r'items\.length\s*>\s*1\)'
    )
    assert call_pattern.search(content), (
        "openFileItem 6th argument must be 'items.length > 1' to conditionally "
        "enable modal navigation only for multi-item lists"
    )


# [pr_diff] fail_to_pass
def test_css_action_bar_uses_broad_selector():
    """CSS action bar hover/focus/select selectors must NOT use .changes-view-body.

    The parent selector must be broad enough to cover all rendering contexts
    (pane body AND modal editor), not just .changes-view-body.
    """
    content = CHANGESVIEW_CSS.read_text()

    # Extract lines containing action bar selectors
    action_bar_lines = [
        line for line in content.splitlines()
        if ".chat-collapsible-list-action-bar" in line
    ]
    assert len(action_bar_lines) >= 4, (
        f"Expected at least 4 action bar CSS rules, found {len(action_bar_lines)}"
    )

    # None of the action bar selectors should use .changes-view-body
    for line in action_bar_lines:
        assert ".changes-view-body" not in line, (
            f"Action bar selector must not use .changes-view-body: {line.strip()}"
        )

    # Verify hover/focus/select states are present for the action bar
    for state in ["hover", "focused", "selected"]:
        matches = [
            line for line in action_bar_lines
            if f".monaco-list-row:{state}" in line or f".monaco-list-row.{state}" in line
        ]
        assert len(matches) >= 1, (
            f"Missing CSS action bar rule for {state} state"
        )


# [pr_diff] fail_to_pass
def test_css_diff_stats_hide_uses_broad_selector():
    """CSS working-set-line-counts hiding selectors must NOT use .changes-view-body."""
    content = CHANGESVIEW_CSS.read_text()

    # Extract lines with diff stats hiding selectors
    diff_stats_lines = [
        line for line in content.splitlines()
        if ".working-set-line-counts" in line
        and ".monaco-list-row" in line
    ]
    assert len(diff_stats_lines) >= 3, (
        f"Expected at least 3 diff stats hiding rules (hover/focus/select), "
        f"found {len(diff_stats_lines)}"
    )

    # None should use .changes-view-body
    for line in diff_stats_lines:
        assert ".changes-view-body" not in line, (
            f"Diff stats selector must not use .changes-view-body: {line.strip()}"
        )

    # Verify all three states are covered
    for state in ["hover", "focused", "selected"]:
        matches = [
            line for line in diff_stats_lines
            if f".monaco-list-row:{state}" in line or f".monaco-list-row.{state}" in line
        ]
        assert len(matches) >= 1, (
            f"Missing CSS diff stats hiding rule for {state} state"
        )


# [pr_diff] fail_to_pass
def test_action_bar_default_hidden():
    """The base action bar rule must hide by default (display: none) with broad selector."""
    content = CHANGESVIEW_CSS.read_text()

    # Find the base action bar rule (not hover/focus/select variant)
    # Pattern: <selector> .monaco-list-row .chat-collapsible-list-action-bar {
    base_rule_pattern = re.compile(
        r'^([^\n]*\.monaco-list-row\s+\.chat-collapsible-list-action-bar\s*\{[^}]*\})',
        re.MULTILINE | re.DOTALL,
    )
    # Simpler: find lines that define the base action bar rule
    lines = content.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (
            ".monaco-list-row" in stripped
            and ".chat-collapsible-list-action-bar" in stripped
            and ":hover" not in stripped
            and ".focused" not in stripped
            and ".selected" not in stripped
            and "{" in stripped
        ):
            # This is the base action bar selector — must not use .changes-view-body
            assert ".changes-view-body" not in stripped, (
                f"Base action bar rule must not use .changes-view-body: {stripped}"
            )
            # Check that display: none is in this rule block
            block = ""
            for j in range(i, min(i + 5, len(lines))):
                block += lines[j]
                if "}" in lines[j]:
                    break
            assert "display: none" in block or "display:none" in block, (
                f"Base action bar rule must set display: none"
            )
            break
    else:
        assert False, "Could not find base action bar CSS rule"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_layering_rules():
    """VS Code module layering rules must still pass (no forbidden cross-layer imports)."""
    r = subprocess.run(
        ["npm", "run", "valid-layers-check"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Layering check failed:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-500:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ 00356ebc69d09b93830f05eb4eabf872d425abdd
def test_css_uses_tabs_not_spaces():
    """Modified CSS selectors must use tabs for indentation, not spaces.

    Rule: 'We use tabs, not spaces.' (.github/copilot-instructions.md line 72)
    """
    content = CHANGESVIEW_CSS.read_text()
    lines = content.splitlines()

    # Check indented lines in the action bar / diff stats sections
    # These are the lines that agents will modify; they must use tabs
    for i, line in enumerate(lines):
        if ".chat-collapsible-list-action-bar" in line or ".working-set-line-counts" in line:
            # Check the following indented lines in the rule block
            for j in range(i + 1, min(i + 5, len(lines))):
                stripped = lines[j]
                if stripped.strip() == "" or stripped.strip() == "}":
                    continue
                if stripped != stripped.lstrip():
                    # Line is indented — must use tabs, not leading spaces
                    indent = stripped[:len(stripped) - len(stripped.lstrip())]
                    assert "\t" in indent and "    " not in indent, (
                        f"Line {j+1} uses spaces for indentation instead of tabs: "
                        f"{stripped!r}"
                    )
