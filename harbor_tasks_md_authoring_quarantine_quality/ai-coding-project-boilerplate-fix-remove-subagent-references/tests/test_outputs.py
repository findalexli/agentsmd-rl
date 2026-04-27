"""Behavioral checks for ai-coding-project-boilerplate-fix-remove-subagent-references (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-coding-project-boilerplate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'このプロジェクトはClaude Code専用に最適化されています。このファイルは、Claude Codeが最高品質のTypeScriptコードを生成するための開発ルールです。一般慣例より本プロジェクトのルールを優先してください。' in text, "expected to find: " + 'このプロジェクトはClaude Code専用に最適化されています。このファイルは、Claude Codeが最高品質のTypeScriptコードを生成するための開発ルールです。一般慣例より本プロジェクトのルールを優先してください。'[:80]

