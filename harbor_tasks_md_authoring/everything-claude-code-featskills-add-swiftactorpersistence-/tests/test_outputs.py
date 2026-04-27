"""Behavioral checks for everything-claude-code-featskills-add-swiftactorpersistence- (markdown_authoring task).

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
    text = _read('skills/swift-actor-persistence/SKILL.md')
    assert 'Patterns for building thread-safe data persistence layers using Swift actors. Combines in-memory caching with file-backed storage, leveraging the actor model to eliminate data races at compile time.' in text, "expected to find: " + 'Patterns for building thread-safe data persistence layers using Swift actors. Combines in-memory caching with file-backed storage, leveraging the actor model to eliminate data races at compile time.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-actor-persistence/SKILL.md')
    assert 'description: Thread-safe data persistence in Swift using actors — in-memory cache with file-backed storage, eliminating data races by design.' in text, "expected to find: " + 'description: Thread-safe data persistence in Swift using actors — in-memory cache with file-backed storage, eliminating data races by design.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-actor-persistence/SKILL.md')
    assert '- **Load synchronously in `init`** — async initializers add complexity with minimal benefit for local files' in text, "expected to find: " + '- **Load synchronously in `init`** — async initializers add complexity with minimal benefit for local files'[:80]

