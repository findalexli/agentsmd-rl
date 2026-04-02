"""
Task: gradio-block-border-inheritance
Repo: gradio-app/gradio @ 01352c78e560c3a6de728a4aec07027e96c27acc
PR:   #12933

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: All checks use regex on Svelte/CSS source because CSS cannot be
executed or imported in Python — regex is the only viable approach here.
"""

import re
from pathlib import Path

REPO = "/repo"
FILE = Path(REPO) / "js/atoms/src/Block.svelte"


def _read_file():
    return FILE.read_text()


def _extract_style(content: str) -> str:
    """Extract <style> block content, strip CSS comments."""
    m = re.search(r"<style[^>]*>(.*?)</style>", content, re.DOTALL)
    assert m, "No <style> block found in Block.svelte"
    return re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.DOTALL)


def _extract_rule_body(style: str, selector_pattern: str) -> str:
    """Extract the body of a CSS rule matching the selector pattern."""
    m = re.search(selector_pattern + r"\s*\{([^}]*)\}", style, re.DOTALL)
    assert m, f"No CSS rule matching {selector_pattern!r}"
    return m.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_is_valid_svelte():
    """Block.svelte must exist and be a valid Svelte component."""
    content = _read_file()
    assert len(content.splitlines()) >= 100, "File too small — likely gutted"
    assert "<script" in content, "Missing <script> section"
    assert "<style" in content, "Missing <style> section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hide_container_no_inherited_border_var():
    """hide-container must NOT set --block-border-width (inherits to children)."""
    content = _read_file()
    style = _extract_style(content)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    # The bug: setting CSS custom properties that child blocks inherit.
    # Use [\w-]* to match hyphenated CSS property names like --block-border-width.
    inherited_vars = re.findall(r"--block[\w-]*border[\w-]*\s*:", hide_body)
    assert not inherited_vars, (
        f"hide-container still sets inherited CSS var(s): {inherited_vars}"
    )


# [pr_diff] fail_to_pass
def test_hide_container_uses_direct_border_zero():
    """hide-container must zero its border directly (not via CSS variable)."""
    content = _read_file()
    style = _extract_style(content)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    has_direct = (
        bool(re.search(r"(?<!-)border-width\s*:\s*0", hide_body))
        or bool(re.search(r"(?<!-)border\s*:\s*(?:none|0)", hide_body))
        or bool(re.search(r"(?<!-)border-style\s*:\s*none", hide_body))
    )
    assert has_direct, (
        "hide-container needs a direct border zero (border-width:0, border:none, etc.)"
    )


# [pr_diff] fail_to_pass
def test_child_block_retains_border():
    """Child .block inside hide-container must retain its border.

    The bug: hide-container sets --block-border-width: 0 (a CSS custom property).
    Since custom properties inherit, ALL descendant blocks lose their border.
    The inline style:border-width="var(--block-border-width)" on the element
    references this variable, so it resolves to 0 inside hide-container.

    The fix must ensure hide-container does NOT zero the CSS variable, so
    children's border-width (whether from class rule or inline style) still
    resolves to the theme-provided value.
    """
    content = _read_file()
    style = _extract_style(content)

    # Check if hide-container sets any --block-*border* var (would inherit to children)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    sets_inherited_var = bool(
        re.search(r"--block[\w-]*border[\w-]*\s*:\s*0", hide_body)
    )

    # Check if template uses inline style:border-width referencing the CSS var
    has_inline_border_var = bool(
        re.search(r"style:border-width\s*=", content)
    )

    # If parent zeros the CSS variable AND there's an inline style referencing
    # that variable, children lose their border (inline style wins over class rules,
    # and the inherited variable resolves to 0).
    assert not (sets_inherited_var and has_inline_border_var), (
        "Child block loses border: hide-container zeros --block-border-width "
        "CSS variable, and inline style:border-width references it, so all "
        "descendant blocks get border-width: 0"
    )

    # At least one source of border-width must exist for child blocks
    block_body = _extract_rule_body(style, r"(?<!\w)\.block(?!\w)")
    block_has_border_width = bool(
        re.search(r"(?<!-)border-width\s*:", block_body)
    )
    assert block_has_border_width or has_inline_border_var, (
        "Child block has no source of border-width (neither class rule nor inline style)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_hide_container_preserves_other_resets():
    """hide-container must keep its other CSS resets (margin, box-shadow, etc.)."""
    content = _read_file()
    style = _extract_style(content)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    required = {
        "margin": r"(?<!-)margin\s*:",
        "box-shadow": r"box-shadow\s*:",
        "background": r"background\s*:",
        "padding": r"(?<!-)padding\s*:",
        "overflow": r"overflow\s*:",
    }
    missing = [name for name, pat in required.items() if not re.search(pat, hide_body)]
    assert not missing, f"hide-container missing CSS resets: {missing}"


# [pr_diff] pass_to_pass
def test_block_class_preserves_styling():
    """.block CSS class must retain core visual properties."""
    content = _read_file()
    style = _extract_style(content)
    block_body = _extract_rule_body(style, r"(?<!\w)\.block(?!\w)")
    required = {
        "box-shadow": r"box-shadow\s*:",
        "border-color": r"border-color\s*:",
        "border-radius": r"border-radius\s*:",
        "background": r"background\s*:",
    }
    missing = [name for name, pat in required.items() if not re.search(pat, block_body)]
    assert not missing, f".block CSS missing properties: {missing}"


# [pr_diff] pass_to_pass
def test_svelte_template_integrity():
    """Key Svelte template bindings must be preserved."""
    content = _read_file()
    required = [
        (r"class:hide-container", "class:hide-container binding"),
        (r"class:fullscreen", "class:fullscreen binding"),
        (r"style:flex-grow", "style:flex-grow binding"),
        (r"style:min-width", "style:min-width binding"),
        (r"style:overflow", "style:overflow binding"),
    ]
    missing = [desc for pat, desc in required if not re.search(pat, content)]
    assert not missing, f"Missing template bindings: {missing}"
