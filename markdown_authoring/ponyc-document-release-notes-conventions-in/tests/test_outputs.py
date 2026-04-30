"""Behavioral checks for ponyc-document-release-notes-conventions-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ponyc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Use the `/pony-release-notes` skill if available. Otherwise: create `.release-notes/<slug>.md` (e.g., `fix-foo.md`). Do NOT edit `next-release.md` directly — CI aggregates the individual files. Format' in text, "expected to find: " + 'Use the `/pony-release-notes` skill if available. Otherwise: create `.release-notes/<slug>.md` (e.g., `fix-foo.md`). Do NOT edit `next-release.md` directly — CI aggregates the individual files. Format'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '## Release Notes' in text, "expected to find: " + '## Release Notes'[:80]

