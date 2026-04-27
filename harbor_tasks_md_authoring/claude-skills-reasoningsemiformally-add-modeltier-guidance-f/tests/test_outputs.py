"""Behavioral checks for claude-skills-reasoningsemiformally-add-modeltier-guidance-f (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('reasoning-semiformally/SKILL.md')
    assert '**Smaller models (Haiku-class):** Templates provide the most value. On CVE-2026-29000 (383-line JWT auth bypass), Haiku went from 80% → 100% fault localization with the template (+20pp). The template ' in text, "expected to find: " + '**Smaller models (Haiku-class):** Templates provide the most value. On CVE-2026-29000 (383-line JWT auth bypass), Haiku went from 80% → 100% fault localization with the template (+20pp). The template '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('reasoning-semiformally/SKILL.md')
    assert '**Larger models (Sonnet-class):** Templates can add overhead on bugs the model already handles. Same CVE, Sonnet scored 100% standard but 80% with the template (-20pp). The structured format consumed ' in text, "expected to find: " + '**Larger models (Sonnet-class):** Templates can add overhead on bugs the model already handles. Same CVE, Sonnet scored 100% standard but 80% with the template (-20pp). The structured format consumed '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('reasoning-semiformally/SKILL.md')
    assert '**Cost optimization:** Haiku + semi-formal ≈ Sonnet standard, at ~1/10th the cost. When using sub-agents for verification (e.g., verify_patch), consider Haiku + template instead of Sonnet + standard p' in text, "expected to find: " + '**Cost optimization:** Haiku + semi-formal ≈ Sonnet standard, at ~1/10th the cost. When using sub-agents for verification (e.g., verify_patch), consider Haiku + template instead of Sonnet + standard p'[:80]

