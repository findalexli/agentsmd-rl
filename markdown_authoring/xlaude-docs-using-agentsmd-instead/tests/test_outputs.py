"""Behavioral checks for xlaude-docs-using-agentsmd-instead (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xlaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- macOS: `~/Library/Application Support/com.xuanwo.xlaude/state.json`' in text, "expected to find: " + '- macOS: `~/Library/Application Support/com.xuanwo.xlaude/state.json`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- 启动全局配置的 `agent` 命令（默认：`claude --dangerously-skip-permissions`）' in text, "expected to find: " + '- 启动全局配置的 `agent` 命令（默认：`claude --dangerously-skip-permissions`）'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`agent` 字段用于配置启动会话时使用的完整命令行（全局唯一，对 `open` 和 Dashboard 均生效）：' in text, "expected to find: " + '`agent` 字段用于配置启动会话时使用的完整命令行（全局唯一，对 `open` 和 Dashboard 均生效）：'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

