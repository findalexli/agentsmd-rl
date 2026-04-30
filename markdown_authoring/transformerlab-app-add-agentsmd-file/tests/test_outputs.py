"""Behavioral checks for transformerlab-app-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/transformerlab-app")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Imports**: Use existing patterns in neighboring files; check package.json/pyproject.toml before adding deps' in text, "expected to find: " + '- **Imports**: Use existing patterns in neighboring files; check package.json/pyproject.toml before adding deps'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Frontend test**: `npm test` (Jest); single test: `npm test -- --testPathPattern="<pattern>"`' in text, "expected to find: " + '- **Frontend test**: `npm test` (Jest); single test: `npm test -- --testPathPattern="<pattern>"`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **TypeScript**: ESLint with erb config, Prettier (single quotes), functional components' in text, "expected to find: " + '- **TypeScript**: ESLint with erb config, Prettier (single quotes), functional components'[:80]

