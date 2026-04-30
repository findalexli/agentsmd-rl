"""Behavioral checks for dash_skills-tweaks-to-darttestfundamentals (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dash-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-test-fundamentals/SKILL.md')
    assert '- **NOTE**: DO NOT remove groups when doing a cleanup on existing code you' in text, "expected to find: " + '- **NOTE**: DO NOT remove groups when doing a cleanup on existing code you'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-test-fundamentals/SKILL.md')
    assert "didn't create unless explicitly asked to. This can cause a LOT of churn" in text, "expected to find: " + "didn't create unless explicitly asked to. This can cause a LOT of churn"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-test-fundamentals/SKILL.md')
    assert '- To clean up resources created WITHIN the `test` body, consider using' in text, "expected to find: " + '- To clean up resources created WITHIN the `test` body, consider using'[:80]

