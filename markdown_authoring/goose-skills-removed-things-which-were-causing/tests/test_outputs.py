"""Behavioral checks for goose-skills-removed-things-which-were-causing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/goose-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/capabilities/create-dashboard/SKILL.md')
    assert 'If template initialization fails because the template source is unavailable, tell the user to retry once it is available. Do not hand-roll a replacement template.' in text, "expected to find: " + 'If template initialization fails because the template source is unavailable, tell the user to retry once it is available. Do not hand-roll a replacement template.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/capabilities/create-dashboard/SKILL.md')
    assert '- Dashboard missing but mirror exists: restore from mirror into `$HOME/dashboard`, install deps, build, start server, verify health.' in text, "expected to find: " + '- Dashboard missing but mirror exists: restore from mirror into `$HOME/dashboard`, install deps, build, start server, verify health.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/capabilities/create-dashboard/SKILL.md')
    assert '4. Verify mirror size stays small (roughly under 1 MB; if it grows very large, clean leaked heavy folders and sync again).' in text, "expected to find: " + '4. Verify mirror size stays small (roughly under 1 MB; if it grows very large, clean leaked heavy folders and sync again).'[:80]

