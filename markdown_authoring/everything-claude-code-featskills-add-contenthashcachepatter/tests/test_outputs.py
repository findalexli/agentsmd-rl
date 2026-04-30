"""Behavioral checks for everything-claude-code-featskills-add-contenthashcachepatter (markdown_authoring task).

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
    text = _read('skills/content-hash-cache-pattern/SKILL.md')
    assert 'Cache expensive file processing results (PDF parsing, text extraction, image analysis) using SHA-256 content hashes as cache keys. Unlike path-based caching, this approach survives file moves/renames ' in text, "expected to find: " + 'Cache expensive file processing results (PDF parsing, text extraction, image analysis) using SHA-256 content hashes as cache keys. Unlike path-based caching, this approach survives file moves/renames '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/content-hash-cache-pattern/SKILL.md')
    assert 'description: Cache expensive file processing results using SHA-256 content hashes — path-independent, auto-invalidating, with service layer separation.' in text, "expected to find: " + 'description: Cache expensive file processing results using SHA-256 content hashes — path-independent, auto-invalidating, with service layer separation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/content-hash-cache-pattern/SKILL.md')
    assert '**Why content hash?** File rename/move = cache hit. Content change = automatic invalidation. No index file needed.' in text, "expected to find: " + '**Why content hash?** File rename/move = cache hit. Content change = automatic invalidation. No index file needed.'[:80]

