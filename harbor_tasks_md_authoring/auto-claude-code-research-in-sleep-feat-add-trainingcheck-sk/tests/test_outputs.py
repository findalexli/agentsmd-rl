"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-trainingcheck-sk (markdown_authoring task).

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
    text = _read('skills/training-check/SKILL.md')
    assert 'description: Periodically check WandB metrics during training to catch problems early (NaN, loss divergence, idle GPUs). Avoids wasting GPU hours on broken runs. Use when training is running and you w' in text, "expected to find: " + 'description: Periodically check WandB metrics during training to catch problems early (NaN, loss divergence, idle GPUs). Avoids wasting GPU hours on broken runs. Use when training is running and you w'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/training-check/SKILL.md')
    assert "- **This skill checks training QUALITY, not process HEALTH.** Process health (session alive, GPU utilization) is [watchdog.py](../../tools/watchdog.py)'s job." in text, "expected to find: " + "- **This skill checks training QUALITY, not process HEALTH.** Process health (session alive, GPU utilization) is [watchdog.py](../../tools/watchdog.py)'s job."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/training-check/SKILL.md')
    assert 'Periodically read WandB metrics during training to catch problems early. Do not wait until training finishes to discover it was a waste of GPU time.' in text, "expected to find: " + 'Periodically read WandB metrics during training to catch problems early. Do not wait until training finishes to discover it was a waste of GPU time.'[:80]

