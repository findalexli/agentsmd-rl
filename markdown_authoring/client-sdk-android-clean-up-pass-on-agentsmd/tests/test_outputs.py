"""Behavioral checks for client-sdk-android-clean-up-pass-on-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/client-sdk-android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Entry types such as `LiveKit` and `ConnectOptions` live in the `io.livekit.android` package alongside these directories.' in text, "expected to find: " + 'Entry types such as `LiveKit` and `ConnectOptions` live in the `io.livekit.android` package alongside these directories.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The SDK is provided through the `livekit-android-sdk` Gradle module (package root `io.livekit.android`).' in text, "expected to find: " + 'The SDK is provided through the `livekit-android-sdk` Gradle module (package root `io.livekit.android`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `io.livekit.android.webrtc` package - convenience extensions on WebRTC types' in text, "expected to find: " + '- `io.livekit.android.webrtc` package - convenience extensions on WebRTC types'[:80]

