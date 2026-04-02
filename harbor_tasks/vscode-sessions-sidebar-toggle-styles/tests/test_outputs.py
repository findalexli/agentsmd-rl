"""
Task: vscode-sessions-sidebar-toggle-styles
Repo: microsoft/vscode @ d11c632ba8e972176f1bfbe1048b41efbad0b691
PR:   306304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
CSS_FILE = Path(f"{REPO}/src/vs/sessions/browser/parts/media/sidebarPart.css")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — structure / syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_css_file_exists():
    """CSS file must exist at the expected path."""
    assert CSS_FILE.exists(), f"CSS file not found: {CSS_FILE}"


# [static] pass_to_pass
def test_css_balanced_braces():
    """CSS must have balanced curly braces (no syntax error)."""
    content = CSS_FILE.read_text()
    open_count = content.count("{")
    close_count = content.count("}")
    assert open_count == close_count, (
        f"CSS has unbalanced braces: {open_count} open, {close_count} close"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_checked_selector_exists():
    """A CSS rule targeting .action-label.checked must be defined."""
    content = CSS_FILE.read_text()
    assert ".action-label.checked" in content, (
        "No .action-label.checked selector found in CSS"
    )


# [pr_diff] fail_to_pass
def test_checked_selector_active_background():
    """Checked state must set background to --vscode-toolbar-activeBackground."""
    content = CSS_FILE.read_text()
    # Match the base .action-label.checked rule block (not :hover/:focus variants)
    match = re.search(
        r"\.action-label\.checked\s*\{([^}]*)\}",
        content,
        re.DOTALL,
    )
    assert match is not None, "No .action-label.checked { ... } rule block found"
    assert "var(--vscode-toolbar-activeBackground)" in match.group(1), (
        "Checked state rule does not set background: var(--vscode-toolbar-activeBackground)"
    )


# [pr_diff] fail_to_pass
def test_checked_selector_border_radius():
    """Checked state must set border-radius to --vscode-cornerRadius-medium."""
    content = CSS_FILE.read_text()
    match = re.search(
        r"\.action-label\.checked\s*\{([^}]*)\}",
        content,
        re.DOTALL,
    )
    assert match is not None, "No .action-label.checked { ... } rule block found"
    assert "var(--vscode-cornerRadius-medium)" in match.group(1), (
        "Checked state rule does not set border-radius: var(--vscode-cornerRadius-medium)"
    )


# [pr_diff] fail_to_pass
def test_hover_focus_preserve_background():
    """Hover and focus pseudo-states of checked must also set the active background."""
    content = CSS_FILE.read_text()
    # Hover: selector ends with .action-label.checked:hover (possibly combined with :focus)
    hover_match = re.search(
        r"\.action-label\.checked:hover[^{]*\{([^}]*)\}",
        content,
        re.DOTALL,
    )
    assert hover_match is not None, "No .action-label.checked:hover rule found"
    assert "var(--vscode-toolbar-activeBackground)" in hover_match.group(1), (
        "Hover state does not preserve active background"
    )
    # Focus
    focus_match = re.search(
        r"\.action-label\.checked:focus[^{]*\{([^}]*)\}",
        content,
        re.DOTALL,
    )
    assert focus_match is not None, "No .action-label.checked:focus rule found"
    assert "var(--vscode-toolbar-activeBackground)" in focus_match.group(1), (
        "Focus state does not preserve active background"
    )


# [pr_diff] fail_to_pass
def test_selector_scoped_to_agent_sessions_sidebar():
    """Checked state selector must be scoped to .agent-sessions-workbench .part.sidebar."""
    content = CSS_FILE.read_text()
    assert re.search(
        r"\.agent-sessions-workbench\s+\.part\.sidebar.*\.action-label\.checked",
        content,
    ), (
        "Checked state selector is not scoped to .agent-sessions-workbench .part.sidebar"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ d11c632ba8e972176f1bfbe1048b41efbad0b691
def test_css_uses_tabs_not_spaces():
    """CSS indentation must use tabs, not spaces.

    Structural check (CSS text analysis — not executable code):
    Rule from .github/copilot-instructions.md:72 "We use tabs, not spaces."
    """
    content = CSS_FILE.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        if line and line[0] == " ":
            raise AssertionError(
                f"Line {i} uses space indentation (expected tab): {line!r}"
            )
