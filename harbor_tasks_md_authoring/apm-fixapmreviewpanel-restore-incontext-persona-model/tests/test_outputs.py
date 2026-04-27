"""Behavioral checks for apm-fixapmreviewpanel-restore-incontext-persona-model (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/apm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.apm/skills/apm-review-panel/SKILL.md')
    assert '(progressive-disclosure skill model -- no sub-agent dispatch). Routing' in text, "expected to find: " + '(progressive-disclosure skill model -- no sub-agent dispatch). Routing'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.apm/skills/apm-review-panel/SKILL.md')
    assert 'chooses *which* lenses execute; it never changes which headings appear' in text, "expected to find: " + 'chooses *which* lenses execute; it never changes which headings appear'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.apm/skills/apm-review-panel/SKILL.md')
    assert 'The panel is fixed at **5 mandatory specialist lenses + 1 conditional' in text, "expected to find: " + 'The panel is fixed at **5 mandatory specialist lenses + 1 conditional'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/apm-review-panel/SKILL.md')
    assert '(progressive-disclosure skill model -- no sub-agent dispatch). Routing' in text, "expected to find: " + '(progressive-disclosure skill model -- no sub-agent dispatch). Routing'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/apm-review-panel/SKILL.md')
    assert 'chooses *which* lenses execute; it never changes which headings appear' in text, "expected to find: " + 'chooses *which* lenses execute; it never changes which headings appear'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/apm-review-panel/SKILL.md')
    assert 'The panel is fixed at **5 mandatory specialist lenses + 1 conditional' in text, "expected to find: " + 'The panel is fixed at **5 mandatory specialist lenses + 1 conditional'[:80]

