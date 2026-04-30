"""Behavioral checks for gh-aw-docs-update-dictation-skill-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gh-aw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dictation/SKILL.md')
    assert 'Fix speech-to-text errors in dictated text for GitHub Agentic Workflows (gh-aw), a GitHub CLI extension that transforms natural language markdown files into GitHub Actions.' in text, "expected to find: " + 'Fix speech-to-text errors in dictated text for GitHub Agentic Workflows (gh-aw), a GitHub CLI extension that transforms natural language markdown files into GitHub Actions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dictation/SKILL.md')
    assert 'GitHub Agentic Workflows (gh-aw) is a Go-based GitHub CLI extension for writing agentic workflows in natural language using markdown files, running them as GitHub Actions.' in text, "expected to find: " + 'GitHub Agentic Workflows (gh-aw) is a Go-based GitHub CLI extension for writing agentic workflows in natural language using markdown files, running them as GitHub Actions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dictation/SKILL.md')
    assert 'description: Fix speech-to-text errors in dictated text using project-specific vocabulary from GitHub Agentic Workflows' in text, "expected to find: " + 'description: Fix speech-to-text errors in dictated text using project-specific vocabulary from GitHub Agentic Workflows'[:80]

