"""Behavioral checks for swift-concurrency-agent-skill-feat-improve-skill-description (markdown_authoring task).

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
    assert "description: 'Diagnose data races, convert callback-based code to async/await, implement actor isolation patterns, resolve Sendable conformance issues, and guide Swift 6 migration. Use when developers" in text, "expected to find: " + "description: 'Diagnose data races, convert callback-based code to async/await, implement actor isolation patterns, resolve Sendable conformance issues, and guide Swift 6 migration. Use when developers"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert '6. For migration work, optimize for minimal blast radius (small, reviewable changes) and follow the validation loop: **Build → Fix errors → Rebuild → Only proceed when clean**.' in text, "expected to find: " + '6. For migration work, optimize for minimal blast radius (small, reviewable changes) and follow the validation loop: **Build → Fix errors → Rebuild → Only proceed when clean**.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert 'Concurrency behavior depends on build settings. Before advising, determine these via `Read` on `Package.swift` or `Grep` in `.pbxproj` files:' in text, "expected to find: " + 'Concurrency behavior depends on build settings. Before advising, determine these via `Read` on `Package.swift` or `Grep` in `.pbxproj` files:'[:80]

