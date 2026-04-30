"""Behavioral checks for xcpcio-docs-add-git-workflow-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xcpcio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'gh pr create --title "<type>: <description>" --body "Brief summary of changes"' in text, "expected to find: " + 'gh pr create --title "<type>: <description>" --body "Brief summary of changes"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Make changes, format, and commit with proper format and signoff' in text, "expected to find: " + '# Make changes, format, and commit with proper format and signoff'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# fix: resolve search filter not working with special characters' in text, "expected to find: " + '# fix: resolve search filter not working with special characters'[:80]

