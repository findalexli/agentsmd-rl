"""Behavioral checks for pinme-add-router-mode-check-section (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pinme")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pinme/SKILL.md')
    assert 'Before building a frontend project for IPFS deployment, ensure it uses **hash mode** routing (e.g., `/#/about`). History mode (e.g., `/about`) will cause **404 errors** on sub-routes when deployed to ' in text, "expected to find: " + 'Before building a frontend project for IPFS deployment, ensure it uses **hash mode** routing (e.g., `/#/about`). History mode (e.g., `/about`) will cause **404 errors** on sub-routes when deployed to '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pinme/SKILL.md')
    assert '- **Vue**: Use `createWebHashHistory()` instead of `createWebHistory()`' in text, "expected to find: " + '- **Vue**: Use `createWebHashHistory()` instead of `createWebHistory()`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pinme/SKILL.md')
    assert '- **React**: Use `HashRouter` instead of `BrowserRouter`' in text, "expected to find: " + '- **React**: Use `HashRouter` instead of `BrowserRouter`'[:80]

