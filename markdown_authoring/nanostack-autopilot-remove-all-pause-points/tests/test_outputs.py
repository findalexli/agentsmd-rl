"""Behavioral checks for nanostack-autopilot-remove-all-pause-points (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '**If AUTOPILOT is active:** Present the plan briefly and proceed immediately. Do not wait for approval. The user chose autopilot because they trust the process.' in text, "expected to find: " + '**If AUTOPILOT is active:** Present the plan briefly and proceed immediately. Do not wait for approval. The user chose autopilot because they trust the process.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '**Otherwise:** Present the plan to the user. Wait for explicit approval before executing. If the user modifies the plan, update it before proceeding.' in text, "expected to find: " + '**Otherwise:** Present the plan to the user. Wait for explicit approval before executing. If the user modifies the plan, update it before proceeding.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert 'After the plan is approved (or auto-approved in autopilot), do these two steps in order:' in text, "expected to find: " + 'After the plan is approved (or auto-approved in autopilot), do these two steps in order:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**If AUTOPILOT is active:** Skip this question. Go directly to Next Step (compound + sprint summary). The user will decide how to run it after the sprint closes.' in text, "expected to find: " + '**If AUTOPILOT is active:** Skip this question. Go directly to Next Step (compound + sprint summary). The user will decide how to run it after the sprint closes.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**Step 2: How to see the result.**' in text, "expected to find: " + '**Step 2: How to see the result.**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**Otherwise**, ask:' in text, "expected to find: " + '**Otherwise**, ask:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '**If AUTOPILOT is active:** Do NOT ask clarifying questions. Work with the information provided. Default to Builder mode. If the description is clear enough to plan, skip the diagnostic questions and ' in text, "expected to find: " + '**If AUTOPILOT is active:** Do NOT ask clarifying questions. Work with the information provided. Default to Builder mode. If the description is clear enough to plan, skip the diagnostic questions and '[:80]

