"""Behavioral checks for xiaohongshu-mcp-docs-update-claudemd-with-development (markdown_authoring task).

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
    assert '- 我需要: 1.本地 review; 2.远程 PR review.' in text, "expected to find: " + '- 我需要: 1.本地 review; 2.远程 PR review.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 测试过程中产生的脚本和build中间文件,如果没有必要,则删除.' in text, "expected to find: " + '- 测试过程中产生的脚本和build中间文件,如果没有必要,则删除.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 所有的feature变更,都需要使用分支进行开发.' in text, "expected to find: " + '- 所有的feature变更,都需要使用分支进行开发.'[:80]

