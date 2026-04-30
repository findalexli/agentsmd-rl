"""Behavioral checks for nemoclaw-docsskills-update-skills-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nemoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/nemoclaw-skills-guide/SKILL.md')
    assert '| `nemoclaw-maintainer-day` | Daytime loop: pick the highest-value version-targeted item and execute the right workflow (merge gate, salvage, security sweep, test gaps, hotspot cooling, or sequencing)' in text, "expected to find: " + '| `nemoclaw-maintainer-day` | Daytime loop: pick the highest-value version-targeted item and execute the right workflow (merge gate, salvage, security sweep, test gaps, hotspot cooling, or sequencing)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/nemoclaw-skills-guide/SKILL.md')
    assert "| `nemoclaw-maintainer-morning` | Morning standup: triage the backlog, determine the day's target version, label selected items, surface stragglers, and output the daily plan. |" in text, "expected to find: " + "| `nemoclaw-maintainer-morning` | Morning standup: triage the backlog, determine the day's target version, label selected items, surface stragglers, and output the daily plan. |"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/nemoclaw-skills-guide/SKILL.md')
    assert '| `nemoclaw-maintainer-evening` | End-of-day handoff: check version progress, bump stragglers to the next patch, generate a QA handoff summary, and cut the release tag. |' in text, "expected to find: " + '| `nemoclaw-maintainer-evening` | End-of-day handoff: check version progress, bump stragglers to the next patch, generate a QA handoff summary, and cut the release tag. |'[:80]

