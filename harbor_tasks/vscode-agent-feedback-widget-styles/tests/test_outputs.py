"""
Task: vscode-agent-feedback-widget-styles
Repo: microsoft/vscode @ 39a50d8d3f4cb82f8d23f6ed762d8feda0a8032f

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a TypeScript/CSS repo — checks use static file content analysis.
# AST-only because: TypeScript/CSS files cannot be executed in the test environment
"""

from pathlib import Path

REPO = "/workspace/vscode"
THEME = Path(REPO) / "src/vs/sessions/common/theme.ts"
INPUT_CONTRIB = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts"
WIDGET_CONTRIB = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts"
INPUT_CSS = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css"
WIDGET_CSS = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorWidget.css"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — required files exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_required_files_exist():
    """All modified files must be present in the workspace."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    for p in [THEME, INPUT_CONTRIB, WIDGET_CONTRIB, INPUT_CSS, WIDGET_CSS]:
        assert p.exists(), f"Required file missing: {p}"


# [static] pass_to_pass
def test_copyright_headers_preserved():
    """Microsoft copyright header must remain in all modified TypeScript files."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    for p in [THEME, INPUT_CONTRIB, WIDGET_CONTRIB]:
        header = p.read_text(encoding="utf-8")[:400]
        assert "Copyright" in header, f"Copyright header missing from {p.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_theme_border_uses_editor_widget_border():
    """agentFeedbackInputWidgetBorder must use editorWidgetBorder, not transparent(iconForeground)."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = THEME.read_text(encoding="utf-8")
    assert "editorWidgetBorder" in src, "theme.ts must import/use editorWidgetBorder"
    assert "transparent(iconForeground" not in src, \
        "theme.ts must not use transparent(iconForeground) for the border color"


# [pr_diff] fail_to_pass
def test_icon_foreground_removed_from_theme():
    """iconForeground import must be removed from theme.ts after border fix."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = THEME.read_text(encoding="utf-8")
    assert "iconForeground" not in src, \
        "iconForeground should be removed from theme.ts (replaced by editorWidgetBorder)"


# [pr_diff] fail_to_pass
def test_apply_font_info_removed():
    """applyFontInfo calls must be removed from agentFeedbackEditorInputContribution.ts."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = INPUT_CONTRIB.read_text(encoding="utf-8")
    assert "applyFontInfo" not in src, \
        "applyFontInfo calls should be removed to stop applying monospace editor font to feedback widget"


# [pr_diff] fail_to_pass
def test_animation_keyframes_added():
    """agentFeedbackEditorInput.css must include the agentFeedbackInputAppear keyframe animation."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = INPUT_CSS.read_text(encoding="utf-8")
    assert "@keyframes agentFeedbackInputAppear" in src, \
        "Missing @keyframes agentFeedbackInputAppear animation"
    assert "opacity: 0" in src, "Keyframe must animate from opacity: 0"
    assert "translateY" in src, "Keyframe must animate with translateY"


# [pr_diff] fail_to_pass
def test_reduced_motion_accessibility():
    """agentFeedbackEditorInput.css must include prefers-reduced-motion media query."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = INPUT_CSS.read_text(encoding="utf-8")
    assert "@media (prefers-reduced-motion: reduce)" in src, \
        "Missing prefers-reduced-motion media query for accessibility"
    # Verify the media query actually disables animation
    idx = src.index("prefers-reduced-motion")
    context = src[idx : idx + 200]
    assert "animation: none" in context, \
        "prefers-reduced-motion block must set animation: none"


# [pr_diff] fail_to_pass
def test_font_inherit_in_input_css():
    """textarea and measure elements in agentFeedbackEditorInput.css must use font: inherit."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = INPUT_CSS.read_text(encoding="utf-8")
    count = src.count("font: inherit")
    assert count >= 2, \
        f"Expected at least 2 'font: inherit' declarations (textarea + measure), found {count}"


# [pr_diff] fail_to_pass
def test_comment_icon_in_header():
    """Widget header must include a decorative comment icon with aria-hidden."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = WIDGET_CONTRIB.read_text(encoding="utf-8")
    assert "Codicon.comment" in src, "Comment icon (Codicon.comment) must be added to widget header"
    assert 'aria-hidden' in src, "Comment icon must have aria-hidden attribute for accessibility"
    assert "commentIcon" in src, "Variable 'commentIcon' must exist in widget header setup"


# [pr_diff] fail_to_pass
def test_single_comment_shows_text_not_label():
    """When there is exactly one comment, title must show comment text, not '1 comment' label."""
    # AST-only because: TypeScript/CSS files cannot be executed in the test environment
    src = WIDGET_CONTRIB.read_text(encoding="utf-8")
    # Must use the first comment's text
    assert "this._commentItems[0].text" in src, \
        "_updateTitle must display commentItems[0].text when count === 1"
    # Must not fall back to the old hardcoded "1 comment" localized string
    assert "nls.localize('oneComment'" not in src and 'localize("oneComment"' not in src, \
        "Old '1 comment' localized string must be removed"
