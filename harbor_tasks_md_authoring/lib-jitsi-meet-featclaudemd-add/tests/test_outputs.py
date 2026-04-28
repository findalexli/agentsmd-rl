"""Behavioral checks for lib-jitsi-meet-featclaudemd-add (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lib-jitsi-meet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'New features should be implemented only with TypeScript. When modifying existing JavaScript files, consider converting to TypeScript. The codebase is actively migrating from JavaScript to TypeScript.' in text, "expected to find: " + 'New features should be implemented only with TypeScript. When modifying existing JavaScript files, consider converting to TypeScript. The codebase is actively migrating from JavaScript to TypeScript.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is the JavaScript library for accessing Jitsi Meet server-side deployments. It provides WebRTC functionality, XMPP communication, and media handling for Jitsi Meet clients.' in text, "expected to find: " + 'This is the JavaScript library for accessing Jitsi Meet server-side deployments. It provides WebRTC functionality, XMPP communication, and media handling for Jitsi Meet clients.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Default jitsi-meet dependency: `"lib-jitsi-meet": "https://github.com/jitsi/lib-jitsi-meet/releases/download/v<version>+<commit-hash>/lib-jitsi-meet.tgz"`' in text, "expected to find: " + '- Default jitsi-meet dependency: `"lib-jitsi-meet": "https://github.com/jitsi/lib-jitsi-meet/releases/download/v<version>+<commit-hash>/lib-jitsi-meet.tgz"`'[:80]

