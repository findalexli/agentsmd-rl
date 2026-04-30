"""Behavioral checks for xiaohongshu-mcp-docs-update-claude-md (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xiaohongshu-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 重点：PR 代码中如果出现大量的 JS 注入的行为，要检查一下是否是必须的，如果可以用 Go 的 go-rod 替代的话，则直接评论需要用 go-rod 行为替代。' in text, "expected to find: " + '- 重点：PR 代码中如果出现大量的 JS 注入的行为，要检查一下是否是必须的，如果可以用 Go 的 go-rod 替代的话，则直接评论需要用 go-rod 行为替代。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 使用中文注释，一定要简洁明了.专业名词可以用英文.' in text, "expected to find: " + '- 使用中文注释，一定要简洁明了.专业名词可以用英文.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Project Guidelines' in text, "expected to find: " + '# Project Guidelines'[:80]

