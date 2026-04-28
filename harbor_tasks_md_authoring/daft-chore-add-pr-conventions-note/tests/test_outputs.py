"""Behavioral checks for daft-chore-add-pr-conventions-note (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/daft")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Titles: Conventional Commits (e.g., `feat: ...`); enforced by `.github/workflows/pr-labeller.yml`.' in text, "expected to find: " + '- Titles: Conventional Commits (e.g., `feat: ...`); enforced by `.github/workflows/pr-labeller.yml`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Descriptions: follow `.github/pull_request_template.md`.' in text, "expected to find: " + '- Descriptions: follow `.github/pull_request_template.md`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## PR Conventions' in text, "expected to find: " + '## PR Conventions'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

