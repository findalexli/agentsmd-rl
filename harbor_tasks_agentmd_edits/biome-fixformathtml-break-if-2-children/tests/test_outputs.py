"""
Task: biome-fixformathtml-break-if-2-children
Repo: biomejs/biome @ 883ea1d7748466dac8cec5bec7683b15ecfd37a1
PR:   8833

Fix HTML formatter to break block-like elements with >2 children when at least
one is a visible block-like element. Also adds .claude/skills/prettier-compare/SKILL.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_files_exist():
    """Modified Rust source files must exist and be non-empty."""
    for path in [
        "crates/biome_html_formatter/src/html/lists/element_list.rs",
        "crates/biome_html_formatter/src/utils/css_display.rs",
    ]:
        f = Path(f"{REPO}/{path}")
        assert f.exists(), f"{path} must exist"
        assert f.stat().st_size > 0, f"{path} must be non-empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_block_like_forces_multiline_near_text():
    """element_list.rs must force multiline when a visible block-like element is adjacent to text."""
    content = Path(
        f"{REPO}/crates/biome_html_formatter/src/html/lists/element_list.rs"
    ).read_text()
    # The fix imports CssDisplay and uses is_block_like() to force multiline
    assert "css_display::CssDisplay" in content, \
        "element_list.rs should import CssDisplay from css_display module"
    assert "is_block_like()" in content, \
        "element_list.rs should check is_block_like() for formatting decisions"
    # The fix excludes CssDisplay::None from the block-like force-break
    assert re.search(r"is_block_like\(\).*\n.*CssDisplay::None", content), \
        "element_list.rs should check for block-like AND exclude CssDisplay::None"
    assert "force_multiline = true" in content, \
        "element_list.rs should set force_multiline = true for block-like elements near text"


# [pr_diff] fail_to_pass
def test_display_none_preserves_whitespace():
    """element_list.rs must have explicit handling for CssDisplay::None to skip whitespace insertion."""
    content = Path(
        f"{REPO}/crates/biome_html_formatter/src/html/lists/element_list.rs"
    ).read_text()
    # The fix adds: else if css_display == CssDisplay::None { /* skip */ }
    assert re.search(r"css_display\s*==\s*CssDisplay::None", content), \
        "element_list.rs should have explicit CssDisplay::None handling"


# [pr_diff] fail_to_pass
def test_block_like_hard_break_after_element():
    """element_list.rs must emit hard break after block-like elements followed by text."""
    content = Path(
        f"{REPO}/crates/biome_html_formatter/src/html/lists/element_list.rs"
    ).read_text()
    # The fix checks last_css_display.is_block_like() for post-element breaks
    assert "last_css_display.is_block_like()" in content, \
        "element_list.rs should check last_css_display.is_block_like() for post-element breaks"
    # And uses LineMode::Hard for block-like to text transitions
    assert "Some(LineMode::Hard)" in content, \
        "element_list.rs should use LineMode::Hard for block-like elements followed by text"


# [pr_diff] fail_to_pass

    html_files = list(ws_dir.glob("*.html"))
    # Check there's a fixture with nested block-like elements (like <div>a<div>b</div> c</div>)
    has_block_fixture = any(
        "<div" in f.read_text() and f.read_text().count("<div") >= 2
        for f in html_files
    )
    assert has_block_fixture, \
        "Should have a test fixture with nested block-like elements for the break behavior"

    # Check there's a fixture testing display:none elements (like <meta>)
    has_none_fixture = any(
        "<meta" in f.read_text()
        for f in html_files
    )
    assert has_none_fixture, \
        "Should have a test fixture with a display:none element (like <meta>)"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
