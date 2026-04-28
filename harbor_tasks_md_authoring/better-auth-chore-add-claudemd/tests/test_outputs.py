"""Behavioral checks for better-auth-chore-add-claudemd (markdown_authoring task).

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
    assert 'following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)' in text, "expected to find: " + 'following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '* Do not use runtime-specific feature like `Buffer` in codebase except test,' in text, "expected to find: " + '* Do not use runtime-specific feature like `Buffer` in codebase except test,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'which takes a long time, use `vitest /path/to/<test-file> -t <pattern>` to' in text, "expected to find: " + 'which takes a long time, use `vitest /path/to/<test-file> -t <pattern>` to'[:80]

