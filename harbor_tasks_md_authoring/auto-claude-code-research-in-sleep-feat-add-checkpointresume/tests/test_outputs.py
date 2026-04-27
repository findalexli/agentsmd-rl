"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-checkpointresume (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/research-refine/SKILL.md')
    assert 'Long-running refinement sessions may fail mid-way (e.g., API timeout, context compaction, or session interruption). To avoid losing completed work, persist state to `refine-logs/REFINE_STATE.json` aft' in text, "expected to find: " + 'Long-running refinement sessions may fail mid-way (e.g., API timeout, context compaction, or session interruption). To avoid losing completed work, persist state to `refine-logs/REFINE_STATE.json` aft'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/research-refine/SKILL.md')
    assert '**Checkpoint:** Write `refine-logs/REFINE_STATE.json` with `{"phase": "anchor", "round": 0, "threadId": null, "last_score": null, "last_verdict": null, "status": "in_progress", "timestamp": "<now>"}`.' in text, "expected to find: " + '**Checkpoint:** Write `refine-logs/REFINE_STATE.json` with `{"phase": "anchor", "round": 0, "threadId": null, "last_score": null, "last_verdict": null, "status": "in_progress", "timestamp": "<now>"}`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/research-refine/SKILL.md')
    assert '**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "review", "round": 1, "threadId": "<saved>", "last_score": <parsed>, "last_verdict": "<parsed>", ...}`.' in text, "expected to find: " + '**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "review", "round": 1, "threadId": "<saved>", "last_score": <parsed>, "last_verdict": "<parsed>", ...}`.'[:80]

