"""Behavioral checks for buildwithclaude-improve-tubeify-skill-structure-eval (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tubeify/SKILL.md')
    assert 'Submit a raw recording URL to the Tubeify API and get back a polished, trimmed video with pauses, filler words, and dead air removed automatically.' in text, "expected to find: " + 'Submit a raw recording URL to the Tubeify API and get back a polished, trimmed video with pauses, filler words, and dead air removed automatically.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tubeify/SKILL.md')
    assert '- `remove_fillers` — remove filler words like "um", "uh", "like" (default: `true`)' in text, "expected to find: " + '- `remove_fillers` — remove filler words like "um", "uh", "like" (default: `true`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tubeify/SKILL.md')
    assert 'If the response contains `"status": "error"`, check the wallet address and retry.' in text, "expected to find: " + 'If the response contains `"status": "error"`, check the wallet address and retry.'[:80]

