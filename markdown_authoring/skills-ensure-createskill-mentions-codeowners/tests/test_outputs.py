"""Behavioral checks for skills-ensure-createskill-mentions-codeowners (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-skill/SKILL.md')
    assert "| Missing CODEOWNERS entry | Add entries for both `/plugins/<plugin>/skills/<skill-name>/` and `/tests/<plugin>/<skill-name>/` matching sibling skills' owner pattern |" in text, "expected to find: " + "| Missing CODEOWNERS entry | Add entries for both `/plugins/<plugin>/skills/<skill-name>/` and `/tests/<plugin>/<skill-name>/` matching sibling skills' owner pattern |"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-skill/SKILL.md')
    assert '- [ ] `.github/CODEOWNERS` has entries for the new skill and its test directory' in text, "expected to find: " + '- [ ] `.github/CODEOWNERS` has entries for the new skill and its test directory'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-skill/SKILL.md')
    assert 'Add entries in `.github/CODEOWNERS` for the new skill and its test directory:' in text, "expected to find: " + 'Add entries in `.github/CODEOWNERS` for the new skill and its test directory:'[:80]

