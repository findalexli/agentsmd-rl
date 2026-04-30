"""Behavioral checks for swift-concurrency-agent-skill-add-quickfix-mode-and-escalati (markdown_authoring task).

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
    assert '- **Background work**: for work that should always hop off the caller’s isolation, move expensive work into an `async` function marked `@concurrent`; for work that doesn’t touch isolated state but can' in text, "expected to find: " + '- **Background work**: for work that should always hop off the caller’s isolation, move expensive work into an `async` function marked `@concurrent`; for work that doesn’t touch isolated state but can'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert '- Then: follow the Quick Fix Playbook entry for actor-isolated protocol conformance and `references/actors.md` for implementation patterns (isolated conformances, `nonisolated` requirements, and escal' in text, "expected to find: " + '- Then: follow the Quick Fix Playbook entry for actor-isolated protocol conformance and `references/actors.md` for implementation patterns (isolated conformances, `nonisolated` requirements, and escal'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('swift-concurrency/SKILL.md')
    assert '- Quick fix: remove `async` if not required; if required by protocol/override/@concurrent, use narrow suppression with rationale. See `references/linting.md`.' in text, "expected to find: " + '- Quick fix: remove `async` if not required; if required by protocol/override/@concurrent, use narrow suppression with rationale. See `references/linting.md`.'[:80]

