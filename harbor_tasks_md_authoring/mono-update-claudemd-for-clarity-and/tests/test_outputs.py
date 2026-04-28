"""Behavioral checks for mono-update-claudemd-for-clarity-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mono")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "1. **Optional fields convention**: In this codebase, whenever there's an optional field (marked with `?`), the type is always explicitly defined as `type | undefined`." in text, "expected to find: " + "1. **Optional fields convention**: In this codebase, whenever there's an optional field (marked with `?`), the type is always explicitly defined as `type | undefined`."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Always run TS checks after every change** - Most packages have a `type-check` command that must pass before committing changes.' in text, "expected to find: " + '2. **Always run TS checks after every change** - Most packages have a `type-check` command that must pass before committing changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- You can always explicitly pass `undefined` for optional fields in this codebase' in text, "expected to find: " + '- You can always explicitly pass `undefined` for optional fields in this codebase'[:80]

