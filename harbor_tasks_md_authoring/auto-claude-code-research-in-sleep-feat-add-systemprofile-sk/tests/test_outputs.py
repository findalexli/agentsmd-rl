"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-systemprofile-sk (markdown_authoring task).

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
    text = _read('skills/system-profile/SKILL.md')
    assert 'description: Profile a target (script, process, GPU, memory, interconnect) using external tools and code instrumentation. Produces structured performance reports with actionable recommendations. Use w' in text, "expected to find: " + 'description: Profile a target (script, process, GPU, memory, interconnect) using external tools and code instrumentation. Produces structured performance reports with actionable recommendations. Use w'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/system-profile/SKILL.md')
    assert "You are a profiling assistant. Based on the user's target, choose appropriate profiling strategies, **including writing instrumentation code when needed**, then run profiling, analyze results, and pro" in text, "expected to find: " + "You are a profiling assistant. Based on the user's target, choose appropriate profiling strategies, **including writing instrumentation code when needed**, then run profiling, analyze results, and pro"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/system-profile/SKILL.md')
    assert "Select from external tools and/or code instrumentation as appropriate. Don't limit yourself to the examples below — use whatever makes sense for the target." in text, "expected to find: " + "Select from external tools and/or code instrumentation as appropriate. Don't limit yourself to the examples below — use whatever makes sense for the target."[:80]

