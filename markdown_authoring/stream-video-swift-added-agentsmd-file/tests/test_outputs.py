"""Behavioral checks for stream-video-swift-added-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stream-video-swift")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository hosts Stream’s Swift Video/Calling SDK for Apple platforms. It provides the real‑time audio/video client, call state & signaling, and SwiftUI/UI kit components to build 1:1 and group c' in text, "expected to find: " + 'This repository hosts Stream’s Swift Video/Calling SDK for Apple platforms. It provides the real‑time audio/video client, call state & signaling, and SwiftUI/UI kit components to build 1:1 and group c'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If a sample app exists, use it to validate UI & media flows. Don’t hardcode credentials—use placeholders like YOUR_STREAM_KEY and configure via environment or xcconfig.' in text, "expected to find: " + 'If a sample app exists, use it to validate UI & media flows. Don’t hardcode credentials—use placeholders like YOUR_STREAM_KEY and configure via environment or xcconfig.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in this repository. Human readers are welcome, but this file is written for tools.' in text, "expected to find: " + 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in this repository. Human readers are welcome, but this file is written for tools.'[:80]

