"""Behavioral checks for stream-video-android-add-agentsmd-file-to-the (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stream-video-android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository hosts Stream’s Kotlin-based Video SDK for Android. It delivers call state management, WebRTC signaling, and both Compose and XML UI layers so customers can ship 1:1 calls, rooms, and l' in text, "expected to find: " + 'This repository hosts Stream’s Kotlin-based Video SDK for Android. It delivers call state management, WebRTC signaling, and both Compose and XML UI layers so customers can ship 1:1 calls, rooms, and l'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) collaborating on this Android SDK. Humans are welcome, but the tone is optimized for tools.' in text, "expected to find: " + 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) collaborating on this Android SDK. Humans are welcome, but the tone is optimized for tools.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Base classes: `TestBase` for fast unit tests; `IntegrationTestBase` for end-to-end call flows; use provided helpers for coroutines and event assertions.' in text, "expected to find: " + '- Base classes: `TestBase` for fast unit tests; `IntegrationTestBase` for end-to-end call flows; use provided helpers for coroutines and event assertions.'[:80]

