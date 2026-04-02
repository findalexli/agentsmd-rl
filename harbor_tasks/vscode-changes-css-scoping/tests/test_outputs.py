"""
Task: vscode-changes-css-scoping
Repo: microsoft/vscode @ 96b97550f6c2316dae1e45be6f3f1ce9364bd99d

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts")
CSS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/media/changesView.css")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_syntax_valid():
    """TypeScript file must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(TS_FILE)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"TypeScript syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ts_uses_changes_file_list():
    """TypeScript file must reference 'changes-file-list' class in DOM creation."""
    ts_content = TS_FILE.read_text()
    assert "changes-file-list" in ts_content, \
        "changesView.ts must contain 'changes-file-list'"


# [pr_diff] fail_to_pass
def test_css_uses_changes_file_list():
    """CSS file must have at least 20 occurrences of 'changes-file-list'."""
    css_content = CSS_FILE.read_text()
    count = css_content.count("changes-file-list")
    assert count >= 20, \
        f"changesView.css must have >= 20 occurrences of 'changes-file-list', found {count}"


# [pr_diff] fail_to_pass
def test_no_old_class_in_ts():
    """TypeScript file must not reference the old 'chat-editing-session-list' class."""
    ts_content = TS_FILE.read_text()
    count = ts_content.count("chat-editing-session-list")
    assert count == 0, \
        f"changesView.ts must have 0 occurrences of 'chat-editing-session-list', found {count}"


# [pr_diff] fail_to_pass
def test_no_old_class_in_css():
    """CSS file must not reference the old 'chat-editing-session-list' class."""
    css_content = CSS_FILE.read_text()
    count = css_content.count("chat-editing-session-list")
    assert count == 0, \
        f"changesView.css must have 0 occurrences of 'chat-editing-session-list', found {count}"


# [pr_diff] fail_to_pass
def test_css_standalone_selectors():
    """Key CSS selectors must be standalone (not nested under .changes-view-body parent)."""
    css_content = CSS_FILE.read_text()
    # After the fix, these selectors are de-nested from .changes-view-body
    assert ".changes-file-list .monaco-scrollable-element" in css_content, \
        "CSS must have standalone '.changes-file-list .monaco-scrollable-element' selector"
    assert ".changes-file-list .monaco-list-rows" in css_content, \
        "CSS must have standalone '.changes-file-list .monaco-list-rows' selector"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_css_has_real_rules():
    """CSS file must still contain real style rules (not emptied or trivially stubbed)."""
    css_content = CSS_FILE.read_text()
    assert "overflow: hidden" in css_content, \
        "CSS must still contain 'overflow: hidden' rule under .changes-file-list"
    assert "z-index: 1" in css_content, \
        "CSS must still contain 'z-index: 1' rule under .changes-file-list"
    assert len(css_content.splitlines()) > 200, \
        f"CSS file seems too short ({len(css_content.splitlines())} lines), may have been stripped"
