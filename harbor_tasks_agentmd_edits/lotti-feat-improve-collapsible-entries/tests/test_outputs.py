"""
Task: lotti-feat-improve-collapsible-entries
Repo: matthiasn/lotti @ be8bbfc8f59d502773f05d99b835f122c22b18c1
PR:   2653

Verify: (1) scroll jumpiness fixed with conditional viewport-aware scroll,
        (2) header layout shows date when expanded,
        (3) collapse animation uses SizeTransition,
        (4) AGENTS.md updated with new guidelines, CLAUDE.md created.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/lotti"

DETAILS_WIDGET = Path(REPO) / "lib/features/journal/ui/widgets/entry_details_widget.dart"
HEADER = Path(REPO) / "lib/features/journal/ui/widgets/entry_details/header/entry_detail_header.dart"
COLLAPSIBLE_SECTION = Path(REPO) / "lib/widgets/misc/collapsible_section.dart"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files have balanced braces and parentheses."""
    for path in [DETAILS_WIDGET, HEADER, COLLAPSIBLE_SECTION]:
        src = path.read_text()
        assert src.count("{") == src.count("}"), \
            f"{path.name}: unbalanced braces"
        assert src.count("(") == src.count(")"), \
            f"{path.name}: unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scroll_uses_viewport_check():
    """Scroll after expand must check viewport position, not scroll unconditionally."""
    src = DETAILS_WIDGET.read_text()
    assert "RenderAbstractViewport" in src, \
        "Should use RenderAbstractViewport to check if card is above viewport before scrolling"
    assert "rendering.dart" in src, \
        "Should import flutter/rendering.dart for viewport-aware scroll logic"


# [pr_diff] fail_to_pass
def test_header_shows_date_when_expanded():
    """Expanded collapsible header must show date widget alongside action icons."""
    src = HEADER.read_text()
    count = src.count("EntryDatetimeWidget")
    assert count >= 2, \
        f"Header should show EntryDatetimeWidget in both collapsed and expanded states (found {count})"


# [pr_diff] fail_to_pass
def test_no_duplicate_date_in_body():
    """Date belongs in the header only — not duplicated below image/audio in expanded body."""
    src = DETAILS_WIDGET.read_text()
    assert "datePadding" not in src, \
        "datePadding variable should be removed — date is now shown in the header"


# [pr_diff] fail_to_pass
def test_collapsible_section_top_alignment():
    """AnimatedSize in CollapsibleSection must align to top for downward expansion."""
    src = COLLAPSIBLE_SECTION.read_text()
    assert "Alignment.top" in src, \
        "AnimatedSize should have top alignment so expansion grows downward, not from center"


# [pr_diff] fail_to_pass
def test_size_transition_for_collapse():
    """Collapse animation should use SizeTransition for smooth clip behavior."""
    src = DETAILS_WIDGET.read_text()
    assert "SizeTransition" in src, \
        "Should use SizeTransition (clips from edge) instead of AnimatedSize (squishes content)"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — agent instruction file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
