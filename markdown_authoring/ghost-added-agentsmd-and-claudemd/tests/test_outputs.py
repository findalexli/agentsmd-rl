"""Behavioral checks for ghost-added-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ghost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Always use `yarn` (v1) for all commands.** This repository uses yarn workspaces, not npm.' in text, "expected to find: " + '**Always use `yarn` (v1) for all commands.** This repository uses yarn workspaces, not npm.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'yarn docker:reset              # Reset all Docker volumes (including database) and restart' in text, "expected to find: " + 'yarn docker:reset              # Reset all Docker volumes (including database) and restart'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. `ghost/admin/lib/asset-delivery` copies them to `ghost/core/core/built/admin/assets/*`' in text, "expected to find: " + '2. `ghost/admin/lib/asset-delivery` copies them to `ghost/core/core/built/admin/assets/*`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

