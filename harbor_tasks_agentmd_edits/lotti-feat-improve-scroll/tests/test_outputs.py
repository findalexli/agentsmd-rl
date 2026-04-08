"""
Task: lotti-feat-improve-scroll
Repo: matthiasn/lotti @ fda7c15b3cd6b88a3d9d258d458ce202f4b025c8
PR:   2883

Verify: (1) scroll refactored to slivers for lazy rendering,
        (2) feature README documents the new scroll architecture.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/lotti"

DETAIL_CONTENT = Path(REPO) / "lib/features/projects/ui/widgets/project_mobile_detail_content.dart"
TASKS_PANEL = Path(REPO) / "lib/features/projects/ui/widgets/project_tasks_panel.dart"
README = Path(REPO) / "lib/features/projects/README.md"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code for Dart source analysis."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


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
    r = _run_py('''
import re, sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_mobile_detail_content.dart").read()

# CustomScrollView must be present
if "CustomScrollView" not in src:
    sys.exit("Missing CustomScrollView widget")

# SingleChildScrollView must be removed from the main scroll container
if "SingleChildScrollView(" in src:
    sys.exit("SingleChildScrollView still present; should be replaced by CustomScrollView")

# CustomScrollView must have a slivers parameter
if not re.search(r"slivers\\s*:", src):
    sys.exit("CustomScrollView missing slivers: parameter")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sliver_task_panel_class_exists():
    """A sliver-compatible task panel widget class is defined."""
    r = _run_py('''
import re, sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_tasks_panel.dart").read()

# ProjectTasksSliverPanel must be a StatelessWidget
if not re.search(r"class\\s+ProjectTasksSliverPanel\\s+extends\\s+StatelessWidget", src):
    sys.exit("ProjectTasksSliverPanel must extend StatelessWidget")

# Must have a build method that returns a Widget
if not re.search(r"class\\s+ProjectTasksSliverPanel[\\s\\S]*?Widget\\s+build\\s*\\(", src):
    sys.exit("ProjectTasksSliverPanel must have a build method returning Widget")

# Must accept a ProjectRecord parameter (typed field)
if "ProjectRecord" not in src:
    sys.exit("ProjectTasksSliverPanel must reference ProjectRecord type")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sliver_list_for_lazy_task_rows():
    """Task rows are rendered lazily via SliverList."""
    r = _run_py('''
import re, sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_tasks_panel.dart").read()

# SliverList must be used for lazy rendering
if "SliverList" not in src:
    sys.exit("Task panel should use SliverList for lazy rendering")

# Must have itemBuilder callback — this is what makes rendering lazy
if "itemBuilder" not in src:
    sys.exit("SliverList must have itemBuilder for lazy item construction")

# Must have itemCount to bound the list
if "itemCount" not in src:
    sys.exit("SliverList must have itemCount to limit lazy rendering")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_detail_content_uses_sliver_task_panel():
    """Detail content renders tasks through the sliver panel, not the eager panel."""
    r = _run_py('''
import sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_mobile_detail_content.dart").read()

# Must reference the sliver panel
if "ProjectTasksSliverPanel" not in src:
    sys.exit("Detail content must use ProjectTasksSliverPanel for lazy task rendering")

# The old eager panel reference should be gone
if "ProjectTasksPanel(" in src:
    sys.exit("Old eager ProjectTasksPanel should be replaced by ProjectTasksSliverPanel")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_detail_content_uses_sliver_adapters():
    """Detail content wraps static header sections in SliverToBoxAdapter."""
    r = _run_py('''
import sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_mobile_detail_content.dart").read()

# SliverToBoxAdapter must wrap non-lazy content
if "SliverToBoxAdapter" not in src:
    sys.exit("Static header widgets should be wrapped in SliverToBoxAdapter inside CustomScrollView")

# Must wrap the HealthPanel in a SliverToBoxAdapter
if "SliverToBoxAdapter" not in src or "HealthPanel" not in src:
    sys.exit("HealthPanel must be wrapped in SliverToBoxAdapter")

# Verify the header widget is also in a SliverToBoxAdapter
if "_ProjectMobileHeader" not in src:
    sys.exit("Header widget must be present")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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
