"""Behavioral checks for rsbuild-featcreatersbuild-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rsbuild")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/create-rsbuild/template-common/AGENTS.md')
    assert 'You are an expert in JavaScript, Rsbuild, and web application development. You write maintainable, performant, and accessible code.' in text, "expected to find: " + 'You are an expert in JavaScript, Rsbuild, and web application development. You write maintainable, performant, and accessible code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/create-rsbuild/template-common/AGENTS.md')
    assert '- `npm run preview` - Preview the production build locally' in text, "expected to find: " + '- `npm run preview` - Preview the production build locally'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/create-rsbuild/template-common/AGENTS.md')
    assert '- `npm run build` - Build the app for production' in text, "expected to find: " + '- `npm run build` - Build the app for production'[:80]

