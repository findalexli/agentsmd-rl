"""Behavioral checks for agentrove-docs-expand-claudemd-with-crosscontext (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentrove")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- When state is keyed by an input so render derives a `pending` flag as `stored.input !== currentInput`, the effect must update state for every input value — bailing on falsy inputs (`if (!x) return`)' in text, "expected to find: " + '- When state is keyed by an input so render derives a `pending` flag as `stored.input !== currentInput`, the effect must update state for every input value — bailing on falsy inputs (`if (!x) return`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- For off-screen entities that need fresh state on next mount, patch the cache optimistically during the stream/mutation (`queryClient.setQueryData`) — `invalidateQueries` alone isn't enough since `us" in text, "expected to find: " + "- For off-screen entities that need fresh state on next mount, patch the cache optimistically during the stream/mutation (`queryClient.setQueryData`) — `invalidateQueries` alone isn't enough since `us"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- When a terminal/completion handler needs metadata about the completed entity, capture it at session/handle creation — don't resolve from the currently-viewed entity at completion time; off-screen co" in text, "expected to find: " + "- When a terminal/completion handler needs metadata about the completed entity, capture it at session/handle creation — don't resolve from the currently-viewed entity at completion time; off-screen co"[:80]

