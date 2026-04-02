"""
Task: vscode-sessions-titlebar-padding
Repo: microsoft/vscode @ f8c32042ed5206d294fe73f1a3b2b74cd3f7bb7a

The fix adds a CSS rule that removes left padding on the sessions titlebar
container when the sidebar is visible (controlled by the absence of .nosidebar
workbench class). LAYOUT.md is also updated with documentation and a changelog
entry.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
CSS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css")
DOCS_FILE = Path(f"{REPO}/src/vs/sessions/LAYOUT.md")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sidebar_visible_selector_exists():
    """The nosidebar-conditional CSS selector must be present in the CSS file."""
    css = CSS_FILE.read_text()
    assert ".agent-sessions-workbench:not(.nosidebar)" in css, (
        "Missing CSS selector .agent-sessions-workbench:not(.nosidebar) — "
        "the fix must add a rule that only applies when the sidebar is visible"
    )


# [pr_diff] fail_to_pass
def test_padding_left_zero_when_sidebar_visible():
    """padding-left must be 0 inside the sidebar-visible rule block."""
    css = CSS_FILE.read_text()
    # Extract all rule blocks following the nosidebar selector
    pattern = r"\.agent-sessions-workbench:not\(\.nosidebar\)[^{]*\{([^}]*)\}"
    blocks = re.findall(pattern, css)
    assert blocks, (
        "Selector .agent-sessions-workbench:not(.nosidebar) found but no "
        "rule block follows it"
    )
    found_zero = any("padding-left: 0" in block for block in blocks)
    assert found_zero, (
        "padding-left: 0 not set in any .agent-sessions-workbench:not(.nosidebar) "
        "rule block — sidebar-visible state should have zero left padding"
    )


# [pr_diff] fail_to_pass
def test_css_rule_targets_titlebar_container():
    """The padding-left: 0 rule must be scoped to .agent-sessions-titlebar-container."""
    css = CSS_FILE.read_text()
    # The full selector must chain nosidebar + the container class
    pattern = (
        r"\.agent-sessions-workbench:not\(\.nosidebar\)"
        r"[^{]*agent-sessions-titlebar-container[^{]*\{([^}]*)\}"
    )
    blocks = re.findall(pattern, css)
    assert blocks, (
        "No rule block found that targets both .agent-sessions-workbench:not(.nosidebar) "
        "and .agent-sessions-titlebar-container — the padding rule must be scoped to "
        "the correct container"
    )
    found_zero = any("padding-left: 0" in block for block in blocks)
    assert found_zero, (
        "padding-left: 0 not found in rule scoped to .agent-sessions-titlebar-container"
    )


# [pr_diff] fail_to_pass
def test_layout_md_documents_nosidebar_padding():
    """LAYOUT.md must document the sidebar-aware padding behavior (nosidebar + padding-left)."""
    docs = DOCS_FILE.read_text()
    assert "nosidebar" in docs, (
        "LAYOUT.md missing mention of the nosidebar workbench class — "
        "the fix should be documented in the layout reference"
    )
    assert "padding-left" in docs, (
        "LAYOUT.md missing mention of padding-left — "
        "the padding behavior must be described"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_base_css_rule_preserved():
    """The original .agent-sessions-titlebar-container base rule must still exist."""
    css = CSS_FILE.read_text()
    # Accept both spaced and unspaced brace variants
    has_base = (
        ".agent-sessions-titlebar-container {" in css
        or ".agent-sessions-titlebar-container{" in css
    )
    assert has_base, (
        "Base .agent-sessions-titlebar-container rule is missing — "
        "the fix must not delete existing rules"
    )
