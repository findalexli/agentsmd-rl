"""Behavioral checks for buildwithclaude-featskill-add-aurakit-sonnet-amplified (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/aurakit/SKILL.md')
    assert 'AuraKit transforms a single `/aura` command into a complete production-grade development pipeline with 34 modes, OWASP-complete security, and 75% token reduction.' in text, "expected to find: " + 'AuraKit transforms a single `/aura` command into a complete production-grade development pipeline with 34 modes, OWASP-complete security, and 75% token reduction.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/aurakit/SKILL.md')
    assert 'description: "Sonnet Amplified fullstack engine. 34 modes, SEC-01~15 OWASP security, 13 runtime hooks, 75% token reduction. Install: npx @smorky85/aurakit"' in text, "expected to find: " + 'description: "Sonnet Amplified fullstack engine. 34 modes, SEC-01~15 OWASP security, 13 runtime hooks, 75% token reduction. Install: npx @smorky85/aurakit"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/aurakit/SKILL.md')
    assert '- **13 Runtime Hooks** — Zero-token security enforcement (security-scan, bash-guard, bloat-check, auto-format, etc.)' in text, "expected to find: " + '- **13 Runtime Hooks** — Zero-token security enforcement (security-scan, bash-guard, bloat-check, auto-format, etc.)'[:80]

