"""Behavioral checks for pro-components-agentsmd-pinyin-ranking (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pro-components")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/AGENTS.md')
    assert '- **API 属性排序规则：使用拼音排序（Pinyin Ranking）**' in text, "expected to find: " + '- **API 属性排序规则：使用拼音排序（Pinyin Ranking）**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/AGENTS.md')
    assert '- 所有 API 属性必须按照属性名的拼音顺序排列' in text, "expected to find: " + '- 所有 API 属性必须按照属性名的拼音顺序排列'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/AGENTS.md')
    assert 'pnpm start     # 启动开发服务器' in text, "expected to find: " + 'pnpm start     # 启动开发服务器'[:80]

