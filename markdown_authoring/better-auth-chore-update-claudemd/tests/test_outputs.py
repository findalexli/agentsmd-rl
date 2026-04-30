"""Behavioral checks for better-auth-chore-update-claudemd (markdown_authoring task).

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
    text = _read('CLAUDE.md')
    assert '[Next.js](https://nextjs.org/docs/llms.txt) + [Fumadocs](https://www.fumadocs.dev/llms.txt)' in text, "expected to find: " + '[Next.js](https://nextjs.org/docs/llms.txt) + [Fumadocs](https://www.fumadocs.dev/llms.txt)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to AI assistants (Claude Code, Cursor, etc.)' in text, "expected to find: " + 'This file provides guidance to AI assistants (Claude Code, Cursor, etc.)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '* Do not use runtime-specific feature like `Buffer` in codebase except' in text, "expected to find: " + '* Do not use runtime-specific feature like `Buffer` in codebase except'[:80]

