"""Behavioral checks for compound-engineering-plugin-fixcebrainstorm-distinguish-veri (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-brainstorm/SKILL.md')
    assert '1. **Verify before claiming** — When the brainstorm touches checkable infrastructure (database tables, routes, config files, dependencies, model definitions), read the relevant source files to confirm' in text, "expected to find: " + '1. **Verify before claiming** — When the brainstorm touches checkable infrastructure (database tables, routes, config files, dependencies, model definitions), read the relevant source files to confirm'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-brainstorm/SKILL.md')
    assert '2. **Defer design decisions to planning** — Implementation details like schemas, migration strategies, endpoint structure, or deployment topology belong in planning, not here — unless the brainstorm i' in text, "expected to find: " + '2. **Defer design decisions to planning** — Implementation details like schemas, migration strategies, endpoint structure, or deployment topology belong in planning, not here — unless the brainstorm i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-brainstorm/SKILL.md')
    assert '- Do any requirements claim that infrastructure is absent without that claim having been verified against the codebase? If so, verify now or label as an unverified assumption.' in text, "expected to find: " + '- Do any requirements claim that infrastructure is absent without that claim having been verified against the codebase? If so, verify now or label as an unverified assumption.'[:80]

