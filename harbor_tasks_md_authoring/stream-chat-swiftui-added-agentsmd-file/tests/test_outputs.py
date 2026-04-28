"""Behavioral checks for stream-chat-swiftui-added-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stream-chat-swiftui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repo hosts Stream’s SwiftUI Chat SDK for iOS. It builds on the core client and provides SwiftUI-first chat components (views, view models, modifiers) for messaging apps.' in text, "expected to find: " + 'This repo hosts Stream’s SwiftUI Chat SDK for iOS. It builds on the core client and provides SwiftUI-first chat components (views, view models, modifiers) for messaging apps.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If a sample app target exists in this repo, prefer running that to validate UI changes. Keep demo configs free of credentials and use placeholders like YOUR_STREAM_KEY.' in text, "expected to find: " + 'If a sample app target exists in this repo, prefer running that to validate UI changes. Keep demo configs free of credentials and use placeholders like YOUR_STREAM_KEY.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in this repository. Human readers are welcome, but this file is written for tools.' in text, "expected to find: " + 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in this repository. Human readers are welcome, but this file is written for tools.'[:80]

