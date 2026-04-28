"""Tests for the markdown authoring task on ant-design CLAUDE.md.

These checks verify that the repo-level agent-instruction file CLAUDE.md
has been updated to clarify the Demo 导入规范 section so that
``_semantic*.tsx`` demo files are recognized as an exception that may
import ``.dumi`` site helpers via relative paths, and that ``.dumi/*``
is no longer treated as a TS path alias.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
CLAUDE_MD = REPO / "CLAUDE.md"


def _read_claude_md() -> str:
    assert CLAUDE_MD.exists(), f"CLAUDE.md not found at {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


def test_claude_md_present():
    """CLAUDE.md exists at the repo root."""
    r = subprocess.run(
        ["test", "-f", str(CLAUDE_MD)], capture_output=True, text=True
    )
    assert r.returncode == 0, f"CLAUDE.md missing at {CLAUDE_MD}"


def test_demo_import_section_present():
    """The Demo 导入规范 heading still exists (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-F", "## Demo 导入规范", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, "Demo 导入规范 heading is missing"


def test_semantic_exception_rule_added():
    """A new rule names ``_semantic*.tsx`` as a 语义文档专用 demo exception."""
    r = subprocess.run(
        ["grep", "-F", "_semantic*.tsx` 属于语义文档专用 demo", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (
        "CLAUDE.md should describe `_semantic*.tsx` as 语义文档专用 demo "
        "(exception)."
    )


def test_dumi_helper_paths_added():
    """The exception rule lists `.dumi/hooks/useLocale` as an allowed path."""
    r = subprocess.run(
        ["grep", "-F", ".dumi/hooks/useLocale", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (
        "CLAUDE.md should mention `.dumi/hooks/useLocale` as an allowed "
        "relative-import target for semantic demo files."
    )


def test_dumi_not_alias_clarification_added():
    """A bullet clarifies `.dumi/*` is NOT a generic TS path alias."""
    r = subprocess.run(
        ["grep", "-F", ".dumi/*` 不是仓库通用的 TS 路径别名", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (
        "CLAUDE.md should state that `.dumi/*` is not a generic TS path "
        "alias for the repository."
    )


def test_test_import_section_intact():
    """Adjacent ## Test 导入规范 heading still present (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-F", "## Test 导入规范", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, "## Test 导入规范 heading was unexpectedly removed"


def test_pr_section_intact():
    """The downstream ## PR 规范 section is still in the file (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-F", "## PR 规范", str(CLAUDE_MD)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, "## PR 规范 heading was unexpectedly removed"


def test_demo_import_uses_bullet_list():
    """The Demo 导入规范 section continues to use markdown bullets."""
    text = _read_claude_md()
    start = text.find("## Demo 导入规范")
    assert start != -1, "Demo 导入规范 heading missing"
    end = text.find("## Test 导入规范", start)
    assert end != -1, "Demo 导入规范 section is unbounded"
    section = text[start:end]
    bullets = [ln for ln in section.splitlines() if ln.startswith("- ")]
    assert len(bullets) >= 5, (
        f"Demo 导入规范 section should remain a bullet list with several "
        f"items, found {len(bullets)} bullet lines."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
# Dropped: test_ci_build_project_run_script requires yarn+network (clones repo)
# Dropped: test_ci_test_image_generate_image_snapshots requires node+puppeteer
# Both are unavailable in this Docker image and unnecessary for markdown_authoring.