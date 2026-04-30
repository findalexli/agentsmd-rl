"""Behavioral checks for qtpass-fix-code-quality-findings-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert '# Use an unresolved thread ID from step 1 output (format typically starts with PRRT_)' in text, "expected to find: " + '# Use an unresolved thread ID from step 1 output (format typically starts with PRRT_)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert '# If upstream remote is not set, add it (one-time setup):' in text, "expected to find: " + '# If upstream remote is not set, add it (one-time setup):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-github/SKILL.md')
    assert 'THREAD_ID="PRRT_FROM_STEP_1"' in text, "expected to find: " + 'THREAD_ID="PRRT_FROM_STEP_1"'[:80]

