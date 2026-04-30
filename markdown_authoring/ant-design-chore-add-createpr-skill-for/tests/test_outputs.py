"""Behavioral checks for ant-design-chore-add-createpr-skill-for (markdown_authoring task).

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
    assert "description: Create pull requests for ant-design using the repository's official PR templates. Use when the user asks to create a PR, open a pull request, write PR title/body, summarize branch changes" in text, "expected to find: " + "description: Create pull requests for ant-design using the repository's official PR templates. Use when the user asks to create a PR, open a pull request, write PR title/body, summarize branch changes"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/SKILL.md')
    assert 'gh pr create --repo ant-design/ant-design --base <base> --title "<title>" --body "$(cat <<\'EOF\'' in text, "expected to find: " + 'gh pr create --repo ant-design/ant-design --base <base> --title "<title>" --body "$(cat <<\'EOF\''[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/SKILL.md')
    assert '不要自己改 section 名称，不要删掉模板里已有的主结构。可以删掉模板中的注释和说明性占位文本，但保留最终要提交的 section。' in text, "expected to find: " + '不要自己改 section 名称，不要删掉模板里已有的主结构。可以删掉模板中的注释和说明性占位文本，但保留最终要提交的 section。'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/references/template-notes-and-examples.md')
    assert 'The Select dropdown could jump when the option list changed during search. This PR keeps the scroll position stable after options are updated. No public API changes are introduced.' in text, "expected to find: " + 'The Select dropdown could jump when the option list changed during search. This PR keeps the scroll position stable after options are updated. No public API changes are introduced.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/references/template-notes-and-examples.md')
    assert '- `refactor(Image): extract normalizePlaceholder to usePlaceholderConfig hook`' in text, "expected to find: " + '- `refactor(Image): extract normalizePlaceholder to usePlaceholderConfig hook`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-pr/references/template-notes-and-examples.md')
    assert 'Select 在搜索过程中更新选项后，下拉列表会出现滚动位置跳动。这个 PR 在选项变更后保持滚动位置稳定。不涉及公开 API 变更。' in text, "expected to find: " + 'Select 在搜索过程中更新选项后，下拉列表会出现滚动位置跳动。这个 PR 在选项变更后保持滚动位置稳定。不涉及公开 API 变更。'[:80]

