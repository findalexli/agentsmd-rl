"""Behavioral checks for safe-wallet-monorepo-docs-add-critical-git-workflow (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/safe-wallet-monorepo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**NEVER push directly to `dev` (default branch) or `main` (production branch).**' in text, "expected to find: " + '**NEVER push directly to `dev` (default branch) or `main` (production branch).**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**All tests must pass before committing. Never commit failing code.**' in text, "expected to find: " + '**All tests must pass before committing. Never commit failing code.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Make your changes and ALWAYS run tests before committing' in text, "expected to find: " + '# Make your changes and ALWAYS run tests before committing'[:80]

