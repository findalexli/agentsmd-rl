"""Behavioral checks for efcore-improve-triage-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/efcore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage/SKILL.md')
    assert 'This skill covers triaging and reproducing incoming issues on the Entity Framework Core repository. To do so, read the issue in question (provided as input in the prompt), as well as any linked issues' in text, "expected to find: " + 'This skill covers triaging and reproducing incoming issues on the Entity Framework Core repository. To do so, read the issue in question (provided as input in the prompt), as well as any linked issues'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage/SKILL.md')
    assert '2. Assess whether the issue involves any sort of security concern. If it does, either because the reporting user claims so, or because you suspect there might be a security aspect that the reporting u' in text, "expected to find: " + '2. Assess whether the issue involves any sort of security concern. If it does, either because the reporting user claims so, or because you suspect there might be a security aspect that the reporting u'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage/SKILL.md')
    assert 'The EF repo contains a set of "area" labels that express which part of EF is affected. Area labels always start with an `area-` prefix. You can see the canonical list of area labels at https://github.' in text, "expected to find: " + 'The EF repo contains a set of "area" labels that express which part of EF is affected. Area labels always start with an `area-` prefix. You can see the canonical list of area labels at https://github.'[:80]

