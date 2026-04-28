"""Behavioral checks for scalar-docsrepo-merge-claude-and-agents (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scalar")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When a **Linear ticket** ID (e.g. `DOC-5102`, `ENG-123`) or a **GitHub issue** number/URL is provided in the prompt, instructions, or related Slack thread, link it in the PR so project-management inte' in text, "expected to find: " + 'When a **Linear ticket** ID (e.g. `DOC-5102`, `ENG-123`) or a **GitHub issue** number/URL is provided in the prompt, instructions, or related Slack thread, link it in the PR so project-management inte'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Both strategies externalize dependencies (nothing is bundled into library output). `api-reference` is special because it has both a default build and a standalone build (`vite.standalone.config.ts`) t' in text, "expected to find: " + 'Both strategies externalize dependencies (nothing is bundled into library output). `api-reference` is special because it has both a default build and a standalone build (`vite.standalone.config.ts`) t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When making UI changes, PRs must include visual artifacts (screenshots and/or demo videos) demonstrating impact. Most package dependencies trickle up into three main visual surfaces: `api-reference`, ' in text, "expected to find: " + 'When making UI changes, PRs must include visual artifacts (screenshots and/or demo videos) demonstrating impact. Most package dependencies trickle up into three main visual surfaces: `api-reference`, '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

