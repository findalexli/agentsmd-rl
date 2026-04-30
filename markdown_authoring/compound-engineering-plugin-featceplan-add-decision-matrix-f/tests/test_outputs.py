"""Behavioral checks for compound-engineering-plugin-featceplan-add-decision-matrix-f (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '- **Unchanged invariants:** [Existing APIs, interfaces, or behaviors that this plan explicitly does not change — and how the new work relates to them. Include when the change touches shared surfaces a' in text, "expected to find: " + '- **Unchanged invariants:** [Existing APIs, interfaces, or behaviors that this plan explicitly does not change — and how the new work relates to them. Include when the change touches shared surfaces a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '| Mode/flag combinations or multi-input behavior | Decision matrix (inputs -> outcomes) |' in text, "expected to find: " + '| Mode/flag combinations or multi-input behavior | Decision matrix (inputs -> outcomes) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '| [Risk] | [Low/Med/High] | [Low/Med/High] | [How addressed] |' in text, "expected to find: " + '| [Risk] | [Low/Med/High] | [Low/Med/High] | [How addressed] |'[:80]

