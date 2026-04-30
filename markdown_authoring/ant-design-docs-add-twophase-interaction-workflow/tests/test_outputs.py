"""Behavioral checks for ant-design-docs-add-twophase-interaction-workflow (markdown_authoring task).

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
    text = _read('.claude/skills/issue-reply/SKILL.md')
    assert '**关键原则：先草拟完整方案，等用户讨论确认后再执行。不要未经确认就回复或关闭 issue。**' in text, "expected to find: " + '**关键原则：先草拟完整方案，等用户讨论确认后再执行。不要未经确认就回复或关闭 issue。**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-reply/SKILL.md')
    assert '1. 使用 `gh issue list` 拉取指定范围的 open issues' in text, "expected to find: " + '1. 使用 `gh issue list` 拉取指定范围的 open issues'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-reply/SKILL.md')
    assert '2. 对每个 issue 获取详情（body、comments、labels）' in text, "expected to find: " + '2. 对每个 issue 获取详情（body、comments、labels）'[:80]

