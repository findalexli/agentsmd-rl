"""Behavioral checks for auto-claude-code-research-in-sleep-add-claude-comm-literatur (markdown_authoring task).

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
    text = _read('skills/comm-lit-review/SKILL.md')
    assert 'description: Communications-domain literature review with Claude-style knowledge-base-first retrieval. Use when the task is about communications, wireless, networking, satellite/NTN, Wi-Fi, cellular, ' in text, "expected to find: " + 'description: Communications-domain literature review with Claude-style knowledge-base-first retrieval. Use when the task is about communications, wireless, networking, satellite/NTN, Wi-Fi, cellular, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/comm-lit-review/SKILL.md')
    assert 'If the center of gravity is generic ML architecture research, pure control theory without communications literature, or software/API documentation rather than papers, fall back to a general literature' in text, "expected to find: " + 'If the center of gravity is generic ML architecture research, pure control theory without communications literature, or software/API documentation rather than papers, fall back to a general literature'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/comm-lit-review/SKILL.md')
    assert '4. broader web using primary publisher pages, official conference sites, DOI pages, and author-hosted copies of already-identified formal papers' in text, "expected to find: " + '4. broader web using primary publisher pages, official conference sites, DOI pages, and author-hosted copies of already-identified formal papers'[:80]

