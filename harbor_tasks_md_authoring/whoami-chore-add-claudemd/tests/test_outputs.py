"""Behavioral checks for whoami-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/whoami")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Imperative mood** — write "add search page" not "added search page" or "adds search page"' in text, "expected to find: " + '3. **Imperative mood** — write "add search page" not "added search page" or "adds search page"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Release commits follow a special format with the product name and semver version:' in text, "expected to find: " + 'Release commits follow a special format with the product name and semver version:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This project uses [Conventional Commits](https://www.conventionalcommits.org/).' in text, "expected to find: " + 'This project uses [Conventional Commits](https://www.conventionalcommits.org/).'[:80]

