"""Behavioral checks for saleor-dashboard-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/saleor-dashboard")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- `npm run dev` - Start development server on port 9000 with host binding, ALWAYS run this process in background, if you can't do that ask user" in text, "expected to find: " + "- `npm run dev` - Start development server on port 9000 with host binding, ALWAYS run this process in background, if you can't do that ask user"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `./node_modules/.bin/jest <file_path>` - Run specific test file (recommended for local development, running all tests is slow)' in text, "expected to find: " + '- `./node_modules/.bin/jest <file_path>` - Run specific test file (recommended for local development, running all tests is slow)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `npm run generate` - Generate GraphQL types and hooks, after making changes in queries/mutations or updating schema' in text, "expected to find: " + '- `npm run generate` - Generate GraphQL types and hooks, after making changes in queries/mutations or updating schema'[:80]

