"""Behavioral checks for ant-design-chore-fix-changelog-skill-agentsmd (markdown_authoring task).

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
    text = _read('.agents/skills/changelog-collect/SKILL.md')
    assert '- [Emoji 规范](../../../AGENTS.md#emoji-规范) - 根据 commit 类型自动标记' in text, "expected to find: " + '- [Emoji 规范](../../../AGENTS.md#emoji-规范) - 根据 commit 类型自动标记'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/changelog-collect/SKILL.md')
    assert '- [格式规范](../../../AGENTS.md#格式规范) - 分组、描述、Emoji 规范' in text, "expected to find: " + '- [格式规范](../../../AGENTS.md#格式规范) - 分组、描述、Emoji 规范'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/changelog-collect/SKILL.md')
    assert '- [核心原则](../../../AGENTS.md#核心原则) - 有效性过滤规则' in text, "expected to find: " + '- [核心原则](../../../AGENTS.md#核心原则) - 有效性过滤规则'[:80]

