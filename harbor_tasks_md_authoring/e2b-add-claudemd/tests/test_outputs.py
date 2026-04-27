"""Behavioral checks for e2b-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/e2b")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Default credentials are stored in .env.local in the repository root or inside ~/.e2b/config.json.' in text, "expected to find: " + 'Default credentials are stored in .env.local in the repository root or inside ~/.e2b/config.json.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Run `pnpm run format`, `pnpm run lint` and `pnpm run typecheck` before commiting changes.' in text, "expected to find: " + 'Run `pnpm run format`, `pnpm run lint` and `pnpm run typecheck` before commiting changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Use pnpm for node and poetry for python to install and update dependencies.' in text, "expected to find: " + 'Use pnpm for node and poetry for python to install and update dependencies.'[:80]

