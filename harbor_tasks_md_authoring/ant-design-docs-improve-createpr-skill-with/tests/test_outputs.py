"""Behavioral checks for ant-design-docs-improve-createpr-skill-with (markdown_authoring task).

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
    text = _read('.claude/skills/create-pr/SKILL.md')
    assert '四、真正执行 `gh pr create` 之前，必须先把 `base`、`title`、`body` 给用户确认，确认后才能创建 PR。' in text, "expected to find: " + '四、真正执行 `gh pr create` 之前，必须先把 `base`、`title`、`body` 给用户确认，确认后才能创建 PR。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/SKILL.md')
    assert '更多类型判断、基线分支建议、确认话术与标题示例见 `references/template-notes-and-examples.md`。' in text, "expected to find: " + '更多类型判断、基线分支建议、确认话术与标题示例见 `references/template-notes-and-examples.md`。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/SKILL.md')
    assert '- `git reflog show <current-branch>` 查看是否能看出“从哪条分支 checkout 出来”' in text, "expected to find: " + '- `git reflog show <current-branch>` 查看是否能看出“从哪条分支 checkout 出来”'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/references/template-notes-and-examples.md')
    assert '- PR title: `site: adjust token panel interaction on theme preview page`' in text, "expected to find: " + '- PR title: `site: adjust token panel interaction on theme preview page`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/references/template-notes-and-examples.md')
    assert '- 站点文档、官网页面、主题页、说明文字：`📝 Site / documentation improvement` / `📝 站点、文档改进`' in text, "expected to find: " + '- 站点文档、官网页面、主题页、说明文字：`📝 Site / documentation improvement` / `📝 站点、文档改进`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/references/template-notes-and-examples.md')
    assert '- CI / workflow / action：通常归到 `⏩ Workflow`、`❓ Other`，或标题使用 `ci:`' in text, "expected to find: " + '- CI / workflow / action：通常归到 `⏩ Workflow`、`❓ Other`，或标题使用 `ci:`'[:80]

