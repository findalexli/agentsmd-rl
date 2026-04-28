"""Behavioral checks for docs-update-docsreaderpersonajuniorsysadminmdc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/docs-reader-persona-junior-sysadmin.mdc')
    assert '- Troubleshooting covers the most common errors and provides direct solutions' in text, "expected to find: " + '- Troubleshooting covers the most common errors and provides direct solutions'[:80]

