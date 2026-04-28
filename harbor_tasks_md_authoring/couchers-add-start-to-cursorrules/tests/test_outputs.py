"""Behavioral checks for couchers-add-start-to-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/couchers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Each subproject has its own `.cursorrules` file with specific tooling and style guidelines' in text, "expected to find: " + '- Each subproject has its own `.cursorrules` file with specific tooling and style guidelines'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- `/app/web` - Next.js web frontend (see `/app/web/.cursorrules` for web-specific rules)' in text, "expected to find: " + '- `/app/web` - Next.js web frontend (see `/app/web/.cursorrules` for web-specific rules)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert "- Check the relevant folder's `.cursorrules` for language/framework-specific rules" in text, "expected to find: " + "- Check the relevant folder's `.cursorrules` for language/framework-specific rules"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('app/web/.cursorrules')
    assert "- Remove extra unnecessary style declarations, including anything that's already a default of MUI or the theme" in text, "expected to find: " + "- Remove extra unnecessary style declarations, including anything that's already a default of MUI or the theme"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('app/web/.cursorrules')
    assert '- Use StyledLink.tsx component or import from next/link for links to preserve routing, NOT MUI Link' in text, "expected to find: " + '- Use StyledLink.tsx component or import from next/link for links to preserve routing, NOT MUI Link'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('app/web/.cursorrules')
    assert 'This project uses **yarn** as the package manager. Always use `yarn` commands instead of `npm`:' in text, "expected to find: " + 'This project uses **yarn** as the package manager. Always use `yarn` commands instead of `npm`:'[:80]

