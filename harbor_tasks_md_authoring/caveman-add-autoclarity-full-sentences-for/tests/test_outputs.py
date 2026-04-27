"""Behavioral checks for caveman-add-autoclarity-full-sentences-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/caveman")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman/SKILL.md')
    assert '> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone. To proceed, run:' in text, "expected to find: " + '> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone. To proceed, run:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman/SKILL.md')
    assert '- **Irreversible action confirmation** — deleting data, dropping tables, force-pushing' in text, "expected to find: " + '- **Irreversible action confirmation** — deleting data, dropping tables, force-pushing'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman/SKILL.md')
    assert '- **Security warning** — destructive ops, credential handling, permission changes' in text, "expected to find: " + '- **Security warning** — destructive ops, credential handling, permission changes'[:80]

