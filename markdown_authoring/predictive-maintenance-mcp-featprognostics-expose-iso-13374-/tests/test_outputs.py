"""Behavioral checks for predictive-maintenance-mcp-featprognostics-expose-iso-13374- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/predictive-maintenance-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/prognostics/SKILL.md')
    assert 'Call `detect_signal_degradation_onset(signal_file=..., feature_name="rms", threshold_sigma=3.0)`.' in text, "expected to find: " + 'Call `detect_signal_degradation_onset(signal_file=..., feature_name="rms", threshold_sigma=3.0)`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/prognostics/SKILL.md')
    assert '"RUL", "remaining useful life", "prognosis", "prognostics", "failure prediction",' in text, "expected to find: " + '"RUL", "remaining useful life", "prognosis", "prognostics", "failure prediction",'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/prognostics/SKILL.md')
    assert 'server. Use this skill when the user says "trend analysis", "degradation trend",' in text, "expected to find: " + 'server. Use this skill when the user says "trend analysis", "degradation trend",'[:80]

