"""Behavioral checks for everything-claude-code-featskills-add-swiftprotocolditesting (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-protocol-di-testing/SKILL.md')
    assert 'Patterns for making Swift code testable by abstracting external dependencies (file system, network, iCloud) behind small, focused protocols. Enables deterministic tests without I/O.' in text, "expected to find: " + 'Patterns for making Swift code testable by abstracting external dependencies (file system, network, iCloud) behind small, focused protocols. Enables deterministic tests without I/O.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-protocol-di-testing/SKILL.md')
    assert 'description: Protocol-based dependency injection for testable Swift code — mock file system, network, and external APIs using focused protocols and Swift Testing.' in text, "expected to find: " + 'description: Protocol-based dependency injection for testable Swift code — mock file system, network, and external APIs using focused protocols and Swift Testing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-protocol-di-testing/SKILL.md')
    assert '- **Single Responsibility**: Each protocol should handle one concern — don\'t create "god protocols" with many methods' in text, "expected to find: " + '- **Single Responsibility**: Each protocol should handle one concern — don\'t create "god protocols" with many methods'[:80]

