"""Behavioral checks for developer-kit-feature161-add-adr-drafting-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/developer-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/developer-kit-core/skills/adr-drafting/SKILL.md')
    assert 'Use this skill when a user or agent has decided on a meaningful architectural change and needs to document the rationale, chosen direction, and trade-offs in a new Architecture Decision Record. It fit' in text, "expected to find: " + 'Use this skill when a user or agent has decided on a meaningful architectural change and needs to document the rationale, chosen direction, and trade-offs in a new Architecture Decision Record. It fit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/developer-kit-core/skills/adr-drafting/SKILL.md')
    assert '6. Confirm that this request is for a **new ADR**, not for editing an existing ADR' in text, "expected to find: " + '6. Confirm that this request is for a **new ADR**, not for editing an existing ADR'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/developer-kit-core/skills/adr-drafting/SKILL.md')
    assert '7. Confirm the desired repository language if documentation language is unclear' in text, "expected to find: " + '7. Confirm the desired repository language if documentation language is unclear'[:80]

