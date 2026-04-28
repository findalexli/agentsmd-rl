"""Behavioral checks for mediawiki-skins-citizen-docs-add-test-conventions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mediawiki-skins-citizen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use Arrange-Act-Assert with blank lines separating each phase' in text, "expected to find: " + '- Use Arrange-Act-Assert with blank lines separating each phase'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- JS tests use Vitest (`tests/vitest/`)' in text, "expected to find: " + '- JS tests use Vitest (`tests/vitest/`)'[:80]

