"""Behavioral checks for claude-ai-music-skills-feat-add-lessons-learned-protocol (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-ai-music-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**When you discover a technical issue during production** (pronunciation error, rhyme violation, formatting problem, wrong assumption), don't just fix it — propose a rule to prevent it from happening " in text, "expected to find: " + "**When you discover a technical issue during production** (pronunciation error, rhyme violation, formatting problem, wrong assumption), don't just fix it — propose a rule to prevent it from happening "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Be proactive.** When you correct something manually, ask yourself: "Should this be a rule?" If the answer is yes, propose it immediately. Don\'t wait to be asked.' in text, "expected to find: " + '**Be proactive.** When you correct something manually, ask yourself: "Should this be a rule?" If the answer is yes, propose it immediately. Don\'t wait to be asked.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '5. **Log the lesson** — add the rule to the appropriate file (SKILL.md, CLAUDE.md, genre README, or reference doc)' in text, "expected to find: " + '5. **Log the lesson** — add the rule to the appropriate file (SKILL.md, CLAUDE.md, genre README, or reference doc)'[:80]

