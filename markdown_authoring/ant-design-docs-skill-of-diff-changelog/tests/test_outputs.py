"""Behavioral checks for ant-design-docs-skill-of-diff-changelog (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ant-design")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/changelog-collect/SKILL.md')
    assert '帮助开发者收集 Ant Design 两个版本之间的 Changelog，处理临时文件并更新到官方 CHANGELOG.zh-CN.md 和 CHANGELOG.en-US.md 文件中。' in text, "expected to find: " + '帮助开发者收集 Ant Design 两个版本之间的 Changelog，处理临时文件并更新到官方 CHANGELOG.zh-CN.md 和 CHANGELOG.en-US.md 文件中。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/changelog-collect/SKILL.md')
    assert "git tag --list | grep -v -E '(experimental|alpha|resource)' | sort -V | tail -20" in text, "expected to find: " + "git tag --list | grep -v -E '(experimental|alpha|resource)' | sort -V | tail -20"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/changelog-collect/SKILL.md')
    assert '根据 AGENTS.md 的规范，对 `~changelog.md` 中的条目进行过滤、分组、格式检查，并在必要时进行交互式确认和修改。' in text, "expected to find: " + '根据 AGENTS.md 的规范，对 `~changelog.md` 中的条目进行过滤、分组、格式检查，并在必要时进行交互式确认和修改。'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **英文**：`Emoji 动词 组件名 描述 … [#PR](链接) [@贡献者]`（动词在前，如 Fix / Add / Support / Remove / Disable / Refactor / Improve / Change）例：`🐞 Fix Button reversed \\`hover\\` and \\`active\\` colors for \\`color\\` in dark' in text, "expected to find: " + '- **英文**：`Emoji 动词 组件名 描述 … [#PR](链接) [@贡献者]`（动词在前，如 Fix / Add / Support / Remove / Disable / Refactor / Improve / Change）例：`🐞 Fix Button reversed \\`hover\\` and \\`active\\` colors for \\`color\\` in dark'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **组件名不用反引号**：组件名（如 Modal、Drawer、Button、Upload.Dragger）不使用 `` ` `` 包裹；属性名、API、token 等仍用反引号（如 `picture-card`、`defaultValue`）' in text, "expected to find: " + '- **组件名不用反引号**：组件名（如 Modal、Drawer、Button、Upload.Dragger）不使用 `` ` `` 包裹；属性名、API、token 等仍用反引号（如 `picture-card`、`defaultValue`）'[:80]

