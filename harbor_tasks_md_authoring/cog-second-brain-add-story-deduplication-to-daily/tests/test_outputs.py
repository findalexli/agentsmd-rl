"""Behavioral checks for cog-second-brain-add-story-deduplication-to-daily (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cog-second-brain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daily-brief/SKILL.md')
    assert '2. **Headline match (fallback):** If the URL is different but the headline describes the same event as a previous story, treat as duplicate — this catches the same story reported by different outlets' in text, "expected to find: " + '2. **Headline match (fallback):** If the URL is different but the headline describes the same event as a previous story, treat as duplicate — this catches the same story reported by different outlets'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daily-brief/SKILL.md')
    assert "1. **URL match (primary):** If a candidate story's main source URL already appears in `dedup_urls`, it's a known story" in text, "expected to find: " + "1. **URL match (primary):** If a candidate story's main source URL already appears in `dedup_urls`, it's a known story"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daily-brief/SKILL.md')
    assert '- **Skip** stories already covered unless there is a **material update** (new data, resolution, escalation, reversal)' in text, "expected to find: " + '- **Skip** stories already covered unless there is a **material update** (new data, resolution, escalation, reversal)'[:80]

