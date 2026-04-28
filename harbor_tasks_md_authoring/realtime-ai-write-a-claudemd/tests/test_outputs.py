"""Behavioral checks for realtime-ai-write-a-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/realtime-ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The project uses a **GStreamer-inspired pipeline architecture** where audio/video processing is handled through modular, composable elements. This design enables flexible composition of AI services, c' in text, "expected to find: " + 'The project uses a **GStreamer-inspired pipeline architecture** where audio/video processing is handled through modular, composable elements. This design enables flexible composition of AI services, c'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Realtime AI is a real-time AI framework for building multimodal AI applications with audio/video processing. The architecture supports multiple transport protocols:' in text, "expected to find: " + 'Realtime AI is a real-time AI framework for building multimodal AI applications with audio/video processing. The architecture supports multiple transport protocols:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The framework supports gRPC as an alternative to WebRTC for server-to-server and programmatic integrations:' in text, "expected to find: " + 'The framework supports gRPC as an alternative to WebRTC for server-to-server and programmatic integrations:'[:80]

