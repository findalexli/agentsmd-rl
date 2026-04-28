"""Behavioral checks for gutenberg-create-an-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gutenberg")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   `/lib/compat/wordpress-X.Y/` - Version-specific features (new PHP features usually go here)' in text, "expected to find: " + '-   `/lib/compat/wordpress-X.Y/` - Version-specific features (new PHP features usually go here)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   `/packages/` - JavaScript packages (each has README.md and CHANGELOG.md)' in text, "expected to find: " + '-   `/packages/` - JavaScript packages (each has README.md and CHANGELOG.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   Fix all formatting/linting issues; these are enforced through CI in PRs' in text, "expected to find: " + '-   Fix all formatting/linting issues; these are enforced through CI in PRs'[:80]

