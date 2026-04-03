"""
Task: vscode-changes-css-scoping
Repo: microsoft/vscode @ 96b97550f6c2316dae1e45be6f3f1ce9364bd99d
PR:   306436

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
TS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts")
CSS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/media/changesView.css")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_file_parseable():
    """TypeScript file must exist and be valid (non-empty, has class declarations)."""
    ts_content = TS_FILE.read_text()
    assert len(ts_content.splitlines()) > 100, "TS file seems truncated or empty"
    assert "class ChangesViewPane" in ts_content, "Expected class ChangesViewPane in TS file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ts_uses_changes_file_list():
    """TypeScript file must reference 'changes-file-list' class in DOM creation."""
    ts_content = TS_FILE.read_text()
    # The fix replaces 'chat-editing-session-list' with 'changes-file-list' in two places:
    # 1. $() DOM helper call for listContainer
    # 2. classList.add() call
    matches = re.findall(r"changes-file-list", ts_content)
    assert len(matches) >= 2, (
        f"changesView.ts must contain at least 2 occurrences of 'changes-file-list', found {len(matches)}"
    )


# [pr_diff] fail_to_pass
def test_css_uses_changes_file_list():
    """CSS file must use 'changes-file-list' in selectors (at least 20 occurrences)."""
    css_content = CSS_FILE.read_text()
    count = css_content.count("changes-file-list")
    assert count >= 20, (
        f"changesView.css must have >= 20 occurrences of 'changes-file-list', found {count}"
    )


# [pr_diff] fail_to_pass
def test_no_old_class_in_ts():
    """TypeScript file must not reference the old 'chat-editing-session-list' class."""
    ts_content = TS_FILE.read_text()
    count = ts_content.count("chat-editing-session-list")
    assert count == 0, (
        f"changesView.ts must have 0 occurrences of 'chat-editing-session-list', found {count}"
    )


# [pr_diff] fail_to_pass
def test_no_old_class_in_css():
    """CSS file must not reference the old 'chat-editing-session-list' class."""
    css_content = CSS_FILE.read_text()
    count = css_content.count("chat-editing-session-list")
    assert count == 0, (
        f"changesView.css must have 0 occurrences of 'chat-editing-session-list', found {count}"
    )


# [pr_diff] fail_to_pass
def test_css_standalone_selectors():
    """Key CSS selectors must be standalone (de-nested from .changes-view-body parent)."""
    css_content = CSS_FILE.read_text()
    # After the fix, these selectors start with .changes-file-list directly,
    # NOT nested under .changes-view-body
    standalone_selectors = [
        ".changes-file-list {",
        ".changes-file-list .monaco-scrollable-element",
        ".changes-file-list .monaco-list-rows",
        ".changes-file-list .monaco-tl-twistie",
    ]
    for sel in standalone_selectors:
        assert sel in css_content, f"CSS must have standalone selector: {sel}"

    # Verify the old nested pattern is gone
    nested_pattern = re.compile(r"\.changes-view-body\s+\.changes-file-list\b")
    assert not nested_pattern.search(css_content), (
        "CSS must NOT have .changes-file-list nested under .changes-view-body"
    )


# [pr_diff] fail_to_pass
def test_css_decoration_selectors_updated():
    """Decoration badge and line count selectors must use new class name."""
    css_content = CSS_FILE.read_text()
    # These selectors were all updated from .chat-editing-session-list to .changes-file-list
    expected = [
        ".changes-file-list .changes-decoration-badge",
        ".changes-file-list .working-set-line-counts",
        ".changes-file-list .working-set-lines-added",
        ".changes-file-list .working-set-lines-removed",
    ]
    for sel in expected:
        assert sel in css_content, f"CSS must contain selector: {sel}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_css_has_real_rules():
    """CSS file must still contain real style rules (not emptied or trivially stubbed)."""
    css_content = CSS_FILE.read_text()
    # Verify key properties still exist
    assert "overflow: hidden" in css_content, "CSS must still contain 'overflow: hidden' rule"
    assert "z-index: 1" in css_content, "CSS must still contain 'z-index: 1' rule"
    assert "display: none" in css_content, "CSS must still contain 'display: none' rule"
    assert "padding-left: 0 !important" in css_content, "CSS must still contain twistie padding reset"
    assert len(css_content.splitlines()) > 200, (
        f"CSS file seems too short ({len(css_content.splitlines())} lines), may have been stripped"
    )


# [static] pass_to_pass
def test_ts_has_real_logic():
    """TypeScript file must still contain real component logic (not stubbed)."""
    ts_content = TS_FILE.read_text()
    # Key patterns that must survive the rename
    assert "listContainer" in ts_content, "TS file must still reference listContainer"
    assert "classList.add" in ts_content, "TS file must still have classList.add calls"
    assert "welcomeContainer" in ts_content, "TS file must still have welcomeContainer"
