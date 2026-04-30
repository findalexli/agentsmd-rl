"""Behavioral checks for xiaozhi-client-docs-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xiaozhi-client")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '这是一个基于 TypeScript 的 MCP（Model Context Protocol）客户端，用于连接小智 AI 服务。项目采用模块化架构，具有清晰的关注点分离。' in text, "expected to find: " + '这是一个基于 TypeScript 的 MCP（Model Context Protocol）客户端，用于连接小智 AI 服务。项目采用模块化架构，具有清晰的关注点分离。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `pnpm check:all` - 运行所有质量检查（lint、typecheck、spellcheck、duplicate check）' in text, "expected to find: " + '- `pnpm check:all` - 运行所有质量检查（lint、typecheck、spellcheck、duplicate check）'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **CLI 层** (`src/cli/`) - 使用 Commander.js 的命令行界面' in text, "expected to find: " + '1. **CLI 层** (`src/cli/`) - 使用 Commander.js 的命令行界面'[:80]

