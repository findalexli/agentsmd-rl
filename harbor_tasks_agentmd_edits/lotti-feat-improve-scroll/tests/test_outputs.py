"""
Task: lotti-feat-improve-scroll
Repo: matthiasn/lotti @ fda7c15b3cd6b88a3d9d258d458ce202f4b025c8
PR:   2883

Verify: (1) scroll refactored to slivers for lazy rendering,
        (2) feature README documents the new scroll architecture.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"

DETAIL_CONTENT = Path(REPO) / "lib/features/projects/ui/widgets/project_mobile_detail_content.dart"
TASKS_PANEL = Path(REPO) / "lib/features/projects/ui/widgets/project_tasks_panel.dart"
README = Path(REPO) / "lib/features/projects/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files have balanced braces and parentheses."""
    for path in [DETAIL_CONTENT, TASKS_PANEL]:
        src = path.read_text()
        assert src.count("{") == src.count("}"), \
            f"{path.name}: unbalanced braces"
        assert src.count("(") == src.count(")"), \
            f"{path.name}: unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_custom_scroll_view_in_detail_content():
    """Detail content uses CustomScrollView for sliver-based lazy rendering."""
    src = DETAIL_CONTENT.read_text()
    assert "CustomScrollView" in src, \
        "ProjectMobileDetailContent should use CustomScrollView for lazy scroll rendering"


# [pr_diff] fail_to_pass
def test_sliver_task_panel_class_exists():
    """A sliver-compatible task panel widget class is defined."""
    src = TASKS_PANEL.read_text()
    assert re.search(r"class\s+\w*Sliver\w*Panel\s+extends\s+StatelessWidget", src), \
        "A sliver-based task panel widget should be defined in project_tasks_panel.dart"


# [pr_diff] fail_to_pass
def test_sliver_list_for_lazy_task_rows():
    """Task rows are rendered lazily via SliverList."""
    src = TASKS_PANEL.read_text()
    assert "SliverList" in src, \
        "Task panel should use SliverList for lazy rendering of task rows"


# [pr_diff] fail_to_pass
def test_detail_content_uses_sliver_task_panel():
    """Detail content renders tasks through the sliver panel, not the eager panel."""
    src = DETAIL_CONTENT.read_text()
    assert re.search(r"ProjectTasks\w*Sliver\w*Panel|Sliver\w*Tasks?\w*Panel", src), \
        "Detail content should reference a sliver-based task panel for lazy rendering"


# [pr_diff] fail_to_pass
def test_detail_content_uses_sliver_adapters():
    """Detail content wraps static header sections in SliverToBoxAdapter."""
    src = DETAIL_CONTENT.read_text()
    assert "SliverToBoxAdapter" in src, \
        "Static header widgets should be wrapped in SliverToBoxAdapter inside CustomScrollView"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_sliver_panel_not_stub():
    """Sliver panel has real build logic, not just a placeholder."""
    src = TASKS_PANEL.read_text()
    # Must have both SliverList and a builder/itemBuilder for actual lazy rendering
    assert "SliverList" in src, "Sliver panel must use SliverList"
    assert "itemBuilder" in src or "delegate" in src, \
        "Sliver panel must have an itemBuilder or delegate for rendering items"
    assert "TaskSummaryRow" in src, \
        "Sliver panel must render TaskSummaryRow widgets"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documents new architecture
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
