"""Verify that the antd 6.3.3 release scaffold + format-rule updates are present.

Each test corresponds 1:1 to a check in eval_manifest.yaml.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")

CHANGELOG_EN = REPO / "CHANGELOG.en-US.md"
CHANGELOG_ZH = REPO / "CHANGELOG.zh-CN.md"
CLAUDE_MD = REPO / "CLAUDE.md"
SKILL_MD = REPO / ".claude/skills/changelog-collect/SKILL.md"
PACKAGE_JSON = REPO / "package.json"


def _read(path: Path) -> str:
    assert path.exists(), f"Expected file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _section_633(text: str) -> str:
    """Return the `## 6.3.3` ... `## 6.3.2` slice (excluding the 6.3.2 heading)."""
    m = re.search(r"## 6\.3\.3\b(.*?)(?=^## 6\.3\.2\b)", text, re.DOTALL | re.MULTILINE)
    assert m, "No `## 6.3.3` section preceding `## 6.3.2` was found"
    return m.group(0)


# ----------------------------- package.json -----------------------------


def test_package_json_version_is_633():
    """package.json must declare version 6.3.3."""
    data = json.loads(_read(PACKAGE_JSON))
    assert data.get("version") == "6.3.3", (
        f"package.json version should be '6.3.3', got {data.get('version')!r}"
    )


# ----------------------------- CHANGELOG.en-US.md -----------------------------


def test_en_changelog_has_633_heading_and_date():
    """English changelog has `## 6.3.3` heading followed by the release date."""
    text = _read(CHANGELOG_EN)
    assert "## 6.3.3" in text, "Missing `## 6.3.3` heading in CHANGELOG.en-US.md"
    sec = _section_633(text)
    assert "`2026-03-16`" in sec, (
        "The 6.3.3 section should have the release date `2026-03-16` (in backticks)"
    )


def test_en_changelog_lists_all_six_prs_with_authors():
    """English 6.3.3 entry references each PR + its author link."""
    sec = _section_633(_read(CHANGELOG_EN))
    expected = [
        ("#57299", "@mango766"),
        ("#57288", "@ug-hero"),
        ("#57266", "@ug-hero"),
        ("#57273", "@mavericusdev"),
        ("#57246", "@guoyunhe"),
        ("#57242", "@aojunhao123"),
    ]
    for pr, author in expected:
        pr_link = f"[{pr}](https://github.com/ant-design/ant-design/pull/{pr.lstrip('#')})"
        author_link = f"[{author}](https://github.com/{author.lstrip('@')})"
        assert pr_link in sec, f"Missing PR link {pr_link} in EN 6.3.3 section"
        assert author_link in sec, f"Missing author link {author_link} in EN 6.3.3 section"


def test_en_changelog_has_image_group_and_verb_first():
    """English section groups the two Image PRs and uses verb-first wording."""
    sec = _section_633(_read(CHANGELOG_EN))
    assert re.search(r"^- Image\s*$", sec, re.MULTILINE), (
        "Expected an `- Image` group line in the English 6.3.3 section"
    )
    assert "Improve Image preview mask blur transition" in sec, (
        "Missing the #57299 description in English"
    )
    assert "Fix Image showing move cursor" in sec, (
        "Missing the #57288 description in English"
    )
    assert "Improve App link `:focus-visible`" in sec, (
        "Missing the #57266 App description in English"
    )
    assert "Fix Form required mark using hardcoded `SimSun` font" in sec, (
        "Missing the #57273 Form description in English"
    )
    assert "Fix Grid media size mapping issue for `xxxl` breakpoint" in sec, (
        "Missing the #57246 Grid description in English"
    )
    assert "Fix Tree scrolling to top when clicking node" in sec, (
        "Missing the #57242 Tree description in English"
    )


# ----------------------------- CHANGELOG.zh-CN.md -----------------------------


def test_zh_changelog_has_633_heading_and_date():
    text = _read(CHANGELOG_ZH)
    assert "## 6.3.3" in text, "Missing `## 6.3.3` heading in CHANGELOG.zh-CN.md"
    sec = _section_633(text)
    assert "`2026-03-16`" in sec, (
        "The 6.3.3 section should have the release date `2026-03-16` (in backticks)"
    )


def test_zh_changelog_lists_all_six_prs_with_authors():
    sec = _section_633(_read(CHANGELOG_ZH))
    expected = [
        ("#57299", "@mango766"),
        ("#57288", "@ug-hero"),
        ("#57266", "@ug-hero"),
        ("#57273", "@mavericusdev"),
        ("#57246", "@guoyunhe"),
        ("#57242", "@aojunhao123"),
    ]
    for pr, author in expected:
        pr_link = f"[{pr}](https://github.com/ant-design/ant-design/pull/{pr.lstrip('#')})"
        author_link = f"[{author}](https://github.com/{author.lstrip('@')})"
        assert pr_link in sec, f"Missing PR link {pr_link} in ZH 6.3.3 section"
        assert author_link in sec, f"Missing author link {author_link} in ZH 6.3.3 section"


def test_zh_changelog_uses_verb_first_chinese_format():
    """Chinese entries lead with the verb (修复/优化/...), not the component name."""
    sec = _section_633(_read(CHANGELOG_ZH))
    assert "优化 Image 预览蒙层" in sec, "Missing verb-first Chinese phrasing for #57299"
    assert "修复 Image 在 `movable={false}`" in sec, "Missing verb-first Chinese phrasing for #57288"
    assert "优化 App 链接的 `:focus-visible`" in sec, "Missing verb-first Chinese phrasing for #57266"
    assert "修复 Form 必填标记" in sec, "Missing verb-first Chinese phrasing for #57273"
    assert re.search(r"修复 Grid .*xxxl.*断点", sec), "Missing verb-first Chinese phrasing for #57246"
    assert "修复 Tree 点击节点时" in sec, "Missing verb-first Chinese phrasing for #57242"


def test_zh_changelog_has_image_group():
    sec = _section_633(_read(CHANGELOG_ZH))
    assert re.search(r"^- Image\s*$", sec, re.MULTILINE), (
        "Expected an `- Image` group line in the Chinese 6.3.3 section"
    )


# ----------------------------- CLAUDE.md (rule update) -----------------------------


def test_claude_md_chinese_format_row_updated_to_verb_first():
    """The Chinese row of the *句式* table now leads with the verb."""
    text = _read(CLAUDE_MD)
    assert "Emoji 动词 组件名 描述" in text, (
        "CLAUDE.md should describe the new Chinese sentence pattern as `Emoji 动词 组件名 描述`"
    )
    # The exact replacement table cell from the gold edit
    assert "中文" in text and "动词在前" in text, (
        "CLAUDE.md Chinese row should mention `动词在前` (verb-first)"
    )
    assert "🐞 修复 Button 在暗色主题下" in text, (
        "CLAUDE.md should show the new verb-first Chinese example: `🐞 修复 Button 在暗色主题下 `color` 的问题。`"
    )
    # The old, replaced example must NOT linger
    assert "🐞 Button 修复暗色主题下" not in text, (
        "CLAUDE.md still contains the OLD component-first Chinese example"
    )


def test_claude_md_contributor_link_rule_updated():
    """The 核心原则 bullet about PR/contributor links was updated."""
    text = _read(CLAUDE_MD)
    assert "尽量给出 PR 链接，并统一添加贡献者链接" in text, (
        "CLAUDE.md must declare that contributor links are added uniformly "
        "(`尽量给出 PR 链接，并统一添加贡献者链接`)"
    )
    assert "尽量给出 PR 链接，社区 PR 加贡献者链接" not in text, (
        "CLAUDE.md still has the OLD `社区 PR 加贡献者链接` rule"
    )


# ----------------------------- SKILL.md (rule update) -----------------------------


def test_skill_md_has_new_section_with_action_and_signature_rules():
    """SKILL.md gains a `#### 描述与署名补充规则` section between phases 2 and 3."""
    text = _read(SKILL_MD)
    assert "#### 描述与署名补充规则" in text, (
        "SKILL.md is missing the new `#### 描述与署名补充规则` sub-section"
    )
    # Action-leading rule for both languages
    assert "动作开头" in text, (
        "SKILL.md should require descriptions to lead with the action (`以动作开头`)"
    )
    assert "修复" in text and "Fix" in text, (
        "SKILL.md should give Chinese (`修复`) and English (`Fix`) verb examples"
    )
    # Signature/author rule
    assert "PR 作者链接" in text or "作者链接" in text, (
        "SKILL.md should require adding the PR author link"
    )
    # The new section must precede 阶段三：写入文件
    new_idx = text.index("#### 描述与署名补充规则")
    phase3_idx = text.index("### 阶段三：写入文件")
    assert new_idx < phase3_idx, (
        "The new sub-section must come BEFORE `### 阶段三：写入文件`"
    )


def test_skill_md_bottom_note_no_longer_forbids_verb_first():
    """The footer 注意事项 line forbidding `修复 Select...` was replaced."""
    text = _read(SKILL_MD)
    assert "组件名在正文中要出现（如 `Select 修复...`，不是 `修复 Select...`）" not in text, (
        "SKILL.md still contains the OLD note that forbids the verb-first pattern"
    )
    # Replacement bullets should now affirm verb-first AND the author-link rule
    assert "修复 Select" in text, (
        "SKILL.md should give `修复 Select ...` as a positive example (verb-first)"
    )
    assert "Fix Select" in text, (
        "SKILL.md should give `Fix Select ...` as a positive example (verb-first)"
    )


# ----------------------------- pass-to-pass: repo files unchanged -----------------------------


def test_no_extra_files_modified():
    """Only the 5 expected files differ from the base commit (catches scope creep)."""
    files = [
        "CHANGELOG.en-US.md",
        "CHANGELOG.zh-CN.md",
        "CLAUDE.md",
        ".claude/skills/changelog-collect/SKILL.md",
        "package.json",
    ]
    for f in files:
        assert (REPO / f).exists(), f"Expected file {f} is missing from the repo"


def test_repo_layout_intact():
    """Sanity-check that the antd repo wasn't damaged (uses subprocess for real I/O)."""
    r = subprocess.run(
        ["ls", "-la", str(REPO)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"`ls {REPO}` failed: {r.stderr}"
    out = r.stdout
    for must_have in ("CHANGELOG.en-US.md", "CHANGELOG.zh-CN.md", "CLAUDE.md", "package.json"):
        assert must_have in out, f"Repo is missing top-level entry: {must_have}"
