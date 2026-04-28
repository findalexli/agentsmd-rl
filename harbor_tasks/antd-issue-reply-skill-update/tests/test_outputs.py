"""
Tests for ant-design PR #57121: update issue-reply skill.

This is a markdown_authoring task. The PR edits a single tier-1
agent-instruction file:

    .claude/skills/issue-reply/SKILL.md

The fail_to_pass tests below are STRUCTURAL signal checks that distinguish
the base commit (no fix) from the gold commit (PR applied). The actual
quality eval signal is Track 2 (eval_manifest.yaml.config_edits) judged by
Gemini.
"""
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL = REPO / ".claude/skills/issue-reply/SKILL.md"


def _read_skill() -> str:
    assert SKILL.is_file(), f"Skill file missing at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass — distinctive lines added by PR #57121 must be present.
# ---------------------------------------------------------------------------

def test_added_pr_merged_unreleased_guidance():
    """The new bullet about 'PR merged but version not released' must be present."""
    text = _read_skill()
    expected = "- PR 已合并但新版本未发布 → 告知用户等待新版本发布"
    assert expected in text, (
        "SKILL.md must contain the new guidance bullet:\n"
        f"  {expected}\n"
        "(should be added under the version-check bullet list for Bug reports)"
    )


def test_added_simplified_polite_closing_line():
    """The simplified one-line guidance for closing politely must be present."""
    text = _read_skill()
    expected = "**关闭时保持礼貌，简要说明关闭原因即可。**"
    assert expected in text, (
        "SKILL.md must contain the simplified polite-closing line:\n"
        f"  {expected}"
    )


def test_subprocess_grep_signals_present():
    """End-to-end subprocess check: grep finds both signal lines in the skill file."""
    r1 = subprocess.run(
        ["grep", "-cF", "PR 已合并但新版本未发布 → 告知用户等待新版本发布", str(SKILL)],
        capture_output=True, text=True, timeout=30,
    )
    assert r1.returncode == 0, f"grep failed for added bullet: {r1.stderr}"
    assert int(r1.stdout.strip()) >= 1, "Added bullet not found by grep"

    r2 = subprocess.run(
        ["grep", "-cF", "**关闭时保持礼貌，简要说明关闭原因即可。**", str(SKILL)],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 0, f"grep failed for simplified line: {r2.stderr}"
    assert int(r2.stdout.strip()) >= 1, "Simplified polite-closing line not found by grep"


# ---------------------------------------------------------------------------
# pass_to_pass — structural invariants of SKILL.md must be preserved.
# These pass on the BASE commit (no fix applied) and must continue to pass
# after the gold patch.
# ---------------------------------------------------------------------------

def test_yaml_frontmatter_intact():
    """The skill file must retain a valid YAML frontmatter block at the top."""
    text = _read_skill()
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter (---)"
    end = text.find("\n---\n", 4)
    assert end > 0, "SKILL.md frontmatter must be terminated by '---' on its own line"
    fm = text[4:end]
    # Use subprocess to parse the frontmatter — exercises real Python in a child process.
    r = subprocess.run(
        ["python3", "-c",
         "import sys, yaml; d = yaml.safe_load(sys.stdin.read());"
         " assert isinstance(d, dict);"
         " assert 'name' in d and d['name'];"
         " assert 'description' in d and d['description'];"
         " print('ok')"],
        input=fm, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"YAML frontmatter invalid:\n{r.stderr}\n---\n{fm}"
    assert "ok" in r.stdout


def test_skill_name_unchanged():
    """The skill 'name' identifier must remain 'antd-issue-reply'."""
    text = _read_skill()
    assert "name: antd-issue-reply" in text, (
        "SKILL.md frontmatter 'name' must remain 'antd-issue-reply'"
    )


def test_core_section_headers_preserved():
    """Top-level skill section headers must be preserved (no accidental deletion)."""
    text = _read_skill()
    for header in (
        "# Ant Design Issue 回复规范",
        "## 目标",
        "## 核心原则",
        "## 基本规则",
        "## ⚠️ 语言政策（必须严格执行）",
        "## Issue 类型",
        "## 处理 dosubot 回复",
        "## Issue 分类处理",
        "## Bug vs Feature Request 分类",
        "## 处理重复 Issues",
        "## 关闭 Issues（需谨慎！）",
        "## 禁止承诺",
        "## 何时不回复",
        "## 语气和风格",
        "## 参考资源",
    ):
        assert header in text, f"Missing required section header: {header!r}"


def test_repo_at_correct_base_commit():
    """Sanity: the repo checkout is at the documented base commit."""
    r = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    sha = r.stdout.strip()
    # Either the base commit (nop) or a commit on top of it (gold via solve.sh).
    # If solve.sh used `git apply` the commit doesn't change; verify HEAD == base.
    assert sha == "15df8e60f14be71095dff1640933b92b770e9217", (
        f"Repo HEAD should be the base commit; got {sha}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
# Dropped: test_ci_build_project_run_script, test_ci_test_image_generate_image_snapshots
# — require Node.js/yarn + network at test time; irrelevant for markdown_authoring task.