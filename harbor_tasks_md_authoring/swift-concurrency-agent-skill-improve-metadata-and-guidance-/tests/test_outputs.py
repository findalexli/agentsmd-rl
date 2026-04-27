"""Behavioral checks for swift-concurrency-agent-skill-improve-metadata-and-guidance- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swift-concurrency-agent-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert "7. Course references are for deeper learning only. Use them sparingly and only when they clearly help answer the developer's question." in text, "expected to find: " + "7. Course references are for deeper learning only. Use them sparingly and only when they clearly help answer the developer's question."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert '- Use `Read` on `Package.swift` for SwiftPM settings (tools version, strict concurrency flags, upcoming features)' in text, "expected to find: " + '- Use `Read` on `Package.swift` for SwiftPM settings (tools version, strict concurrency flags, upcoming features)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert '- Use `Grep` for `SWIFT_STRICT_CONCURRENCY` or `SWIFT_DEFAULT_ACTOR_ISOLATION` in `.pbxproj` files' in text, "expected to find: " + '- Use `Grep` for `SWIFT_STRICT_CONCURRENCY` or `SWIFT_DEFAULT_ACTOR_ISOLATION` in `.pbxproj` files'[:80]

