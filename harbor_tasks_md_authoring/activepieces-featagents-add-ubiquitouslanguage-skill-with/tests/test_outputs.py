"""Behavioral checks for activepieces-featagents-add-ubiquitouslanguage-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/activepieces")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ubiquitous-language/SKILL.md')
    assert 'description: Maintains feature documentation in .agents/features/ and performs mandatory feature overlap detection before any new feature is proposed. Also builds a shared domain vocabulary for Active' in text, "expected to find: " + 'description: Maintains feature documentation in .agents/features/ and performs mandatory feature overlap detection before any new feature is proposed. Also builds a shared domain vocabulary for Active'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ubiquitous-language/SKILL.md')
    assert '2. **Components / services / hooks** — use the Glob tool to find files whose names relate to the proposed concept (e.g., `packages/**/*<keyword>*.{ts,tsx}`), then use the Grep tool to search file cont' in text, "expected to find: " + '2. **Components / services / hooks** — use the Glob tool to find files whose names relate to the proposed concept (e.g., `packages/**/*<keyword>*.{ts,tsx}`), then use the Grep tool to search file cont'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ubiquitous-language/SKILL.md')
    assert 'When writing or reviewing code, use only the canonical term from the glossary. If you see a deprecated alias in existing code, inform the user about each occurrence and let them decide whether to rena' in text, "expected to find: " + 'When writing or reviewing code, use only the canonical term from the glossary. If you see a deprecated alias in existing code, inform the user about each occurrence and let them decide whether to rena'[:80]

