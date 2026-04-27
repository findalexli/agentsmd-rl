"""Behavioral checks for marketingskills-feat-add-expert-panel-scoring (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/copy-editing/SKILL.md')
    assert 'Use this after completing the Seven Sweeps for an additional quality gate. For high-stakes copy (landing pages, launch emails, sales pages), a multi-persona expert review catches issues that a single ' in text, "expected to find: " + 'Use this after completing the Seven Sweeps for an additional quality gate. For high-stakes copy (landing pages, launch emails, sales pages), a multi-persona expert review catches issues that a single '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/copy-editing/SKILL.md')
    assert '5. **Re-score after revisions** — iterate until all personas score 7+, with an average of 8+ across the panel' in text, "expected to find: " + '5. **Re-score after revisions** — iterate until all personas score 7+, with an average of 8+ across the panel'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/copy-editing/SKILL.md')
    assert '- Direct response copywriter (offer structure, objection handling, urgency)' in text, "expected to find: " + '- Direct response copywriter (offer structure, objection handling, urgency)'[:80]

