"""Behavioral checks for vibe-skills-featskill-optimize-skillmd-with-mandatory (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Execute from the approved plan. L grade executes serially; XL grade executes waves sequentially with bounded parallel independent units only. Spawned subagent prompts must end with `$vibe`. Bounded sp' in text, "expected to find: " + 'Execute from the approved plan. L grade executes serially; XL grade executes waves sequentially with bounded parallel independent units only. Spawned subagent prompts must end with `$vibe`. Bounded sp'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Produce a structured intent contract containing: goal, deliverable, constraints, acceptance criteria, product acceptance criteria, manual spot checks, completion language policy, delivery truth contra' in text, "expected to find: " + 'Produce a structured intent contract containing: goal, deliverable, constraints, acceptance criteria, product acceptance criteria, manual spot checks, completion language policy, delivery truth contra'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'The governed runtime selects the internal grade after `deep_interview` and before `plan_execute`. User-facing behavior stays the same regardless of host syntax: one governed runtime authority, one fro' in text, "expected to find: " + 'The governed runtime selects the internal grade after `deep_interview` and before `plan_execute`. User-facing behavior stays the same regardless of host syntax: one governed runtime authority, one fro'[:80]

