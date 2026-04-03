"""
Task: lotti-feat-tasks-page-app-bar
Repo: matthiasn/lotti @ 5cb0c3b44893b5e81abd677aeb74692bb66b2138
PR:   2403

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files must not have obvious syntax errors (balanced braces)."""
    for rel_path in [
        "lib/widgets/app_bar/journal_sliver_appbar.dart",
        "lib/features/journal/ui/pages/infinite_journal_page.dart",
        "lib/features/tasks/ui/filtering/task_label_quick_filter.dart",
    ]:
        src = Path(f"{REPO}/{rel_path}").read_text()
        assert src.count("{") == src.count("}"), (
            f"{rel_path}: unbalanced braces ({src.count('{')} open vs {src.count('}')} close)"
        )
        assert src.count("(") == src.count(")"), (
            f"{rel_path}: unbalanced parens ({src.count('(')} open vs {src.count(')')} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_quick_filter_removed_from_appbar():
    """TaskLabelQuickFilter must no longer be rendered inside JournalSliverAppBar."""
    src = Path(
        f"{REPO}/lib/widgets/app_bar/journal_sliver_appbar.dart"
    ).read_text()

    # The import for task_label_quick_filter should be removed
    assert "task_label_quick_filter" not in src, (
        "journal_sliver_appbar.dart still imports task_label_quick_filter — "
        "it should be removed since the widget moved out of the app bar"
    )

    # The widget itself should not be referenced
    assert "TaskLabelQuickFilter" not in src, (
        "journal_sliver_appbar.dart still references TaskLabelQuickFilter — "
        "the quick filter should be moved out of the app bar"
    )


# [pr_diff] fail_to_pass
def test_quick_filter_in_own_sliver():
    """TaskLabelQuickFilter must appear in infinite_journal_page.dart as a separate sliver."""
    src = Path(
        f"{REPO}/lib/features/journal/ui/pages/infinite_journal_page.dart"
    ).read_text()

    # Must import the quick filter widget
    assert "task_label_quick_filter" in src, (
        "infinite_journal_page.dart must import task_label_quick_filter"
    )

    # Must contain TaskLabelQuickFilter widget reference
    assert "TaskLabelQuickFilter" in src, (
        "infinite_journal_page.dart must reference TaskLabelQuickFilter"
    )

    # Must wrap in SliverToBoxAdapter for proper sliver layout
    assert "SliverToBoxAdapter" in src, (
        "TaskLabelQuickFilter must be wrapped in a SliverToBoxAdapter"
    )

    # Must be gated on selectedLabelIds being non-empty
    assert "selectedLabelIds.isNotEmpty" in src, (
        "Quick filter section must only render when selectedLabelIds is not empty"
    )

    # Must have horizontal padding to align with search bar (40px)
    has_padding = bool(re.search(
        r"EdgeInsets\.(fromLTRB\(\s*40|symmetric\(.*horizontal:\s*40)", src
    ))
    assert has_padding, (
        "Quick filter sliver must have horizontal padding (40) to align with search bar"
    )


# [pr_diff] fail_to_pass
def test_quick_filter_redesigned_with_icon_and_count():
    """TaskLabelQuickFilter must show filter icon and count of active filters."""
    src = Path(
        f"{REPO}/lib/features/tasks/ui/filtering/task_label_quick_filter.dart"
    ).read_text()

    # Must have a filter icon (filter_alt, filter_list, or similar)
    has_filter_icon = bool(re.search(r"Icons\.\s*filter", src))
    assert has_filter_icon, (
        "TaskLabelQuickFilter must display a filter icon (e.g., filter_alt_outlined)"
    )

    # Must show count of selected filters in the title
    # The PR adds ($count) or (${selected.length}) or similar
    has_count = bool(re.search(
        r"\(\s*\$count\s*\)|\(\$\{.*?length.*?\}|\(.*?\.length\)", src
    ))
    assert has_count, (
        "TaskLabelQuickFilter title must include the count of active filters"
    )

    # Must use TextButton.icon for the clear button (compact design)
    assert "TextButton.icon" in src, (
        "Clear button should use TextButton.icon for compact design with icon"
    )

    # Must use compact visual density on chips
    assert "VisualDensity.compact" in src, (
        "Chips must use VisualDensity.compact for compact layout"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a section about the active label filters header
    assert "active label filters" in lower, (
        "Tasks README must document the active label filters header section"
    )

    # Must mention key implementation details
    assert "slivertoboxadapter" in lower or "sliver" in lower, (
        "Tasks README should mention the sliver-based placement"
    )

    # Must mention AnimatedSize for the animation behavior
    assert "animatedsize" in lower or "animated" in lower, (
        "Tasks README should document the animation behavior"
    )

    # Must mention compact design elements
    has_compact = "compact" in lower or "visualdensity" in lower
    assert has_compact, (
        "Tasks README should document the compact visual density"
    )


# [config_edit] fail_to_pass

    # Find the section about TaskLabelQuickFilter specifically
    idx = readme.find("TaskLabelQuickFilter")
    assert idx >= 0, "Labels README must mention TaskLabelQuickFilter"

    # Extract a window around the TaskLabelQuickFilter mention (up to next heading or 800 chars)
    section = readme[idx:idx + 800].lower()

    # The PR adds details about the quick filter appearing below the search bar
    assert "below" in section or "search bar" in section or "tasks page" in section, (
        "Labels README must describe where the quick filter appears (below search bar / tasks page)"
    )

    # Must mention animation behavior (AnimatedSize)
    assert "animat" in section, (
        "Labels README must document the animation behavior of the quick filter"
    )

    # Must mention the count display or active filters text
    has_count = "active label" in section or "(n)" in section or "count" in section
    assert has_count, (
        "Labels README must mention the active label filters display"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass

    # The new entry must specifically mention the clipping fix / visibility fix
    # or the app bar change. The base commit has an older "quick label filter" entry
    # but not one about clipping or visibility.
    has_visibility_fix = (
        "no longer clipped" in lower
        or "visible below" in lower
        or ("clipped" in lower and "app bar" in lower)
        or ("label filter" in lower and "visible" in lower)
        or ("filter" in lower and "below" in lower and "search" in lower)
    )
    assert has_visibility_fix, (
        "CHANGELOG must document the label filter visibility/clipping fix "
        "(e.g., 'active label filters are now visible below the search header')"
    )
