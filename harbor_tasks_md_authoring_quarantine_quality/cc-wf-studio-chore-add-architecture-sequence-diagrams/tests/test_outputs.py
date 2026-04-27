"""Behavioral checks for cc-wf-studio-chore-add-architecture-sequence-diagrams (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cc-wf-studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'このセクションでは、cc-wf-studioの主要なデータフローをMermaid形式のシーケンス図で説明します。' in text, "expected to find: " + 'このセクションでは、cc-wf-studioの主要なデータフローをMermaid形式のシーケンス図で説明します。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Components["Components<br/>src/webview/src/components/"]' in text, "expected to find: " + 'Components["Components<br/>src/webview/src/components/"]'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'SlackMsg->>URI: vscode://cc-wf-studio/import?fileId=...' in text, "expected to find: " + 'SlackMsg->>URI: vscode://cc-wf-studio/import?fileId=...'[:80]

