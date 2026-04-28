"""Behavioral checks for better-auth-docs-add-clauderulesreleasemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/better-auth")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/release.md')
    assert 'pnpm bump  # Interactive prompt to select version, creates commit & tag, automatically pushes' in text, "expected to find: " + 'pnpm bump  # Interactive prompt to select version, creates commit & tag, automatically pushes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/release.md')
    assert '7. The release workflow (`.github/workflows/release.yml`) will automatically:' in text, "expected to find: " + '7. The release workflow (`.github/workflows/release.yml`) will automatically:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/release.md')
    assert '* Whether the commit is on `main` or a version branch (`v*.*.x-latest`)' in text, "expected to find: " + '* Whether the commit is on `main` or a version branch (`v*.*.x-latest`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '* Make sure `pnpm format:check`, `pnpm lint` and `pnpm typecheck` pass' in text, "expected to find: " + '* Make sure `pnpm format:check`, `pnpm lint` and `pnpm typecheck` pass'[:80]

