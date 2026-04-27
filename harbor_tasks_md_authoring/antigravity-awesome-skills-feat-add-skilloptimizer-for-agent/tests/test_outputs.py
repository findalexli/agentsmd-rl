"""Behavioral checks for antigravity-awesome-skills-feat-add-skilloptimizer-for-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-optimizer/SKILL.md')
    assert '**Note:** Codex injects skills via context rather than explicit `Skill` tool calls. Skill loading (present in `base_instructions`) does NOT equal active invocation. To detect actual use, search for sk' in text, "expected to find: " + '**Note:** Codex injects skills via context rather than explicit `Skill` tool calls. Skill loading (present in `base_instructions`) does NOT equal active invocation. To detect actual use, search for sk'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-optimizer/SKILL.md')
    assert 'For skills with chronic undertriggering (0 triggers across 5+ sessions where relevant tasks appeared), flag as "compounding risk" — undertriggered skills cannot self-improve through usage feedback, ca' in text, "expected to find: " + 'For skills with chronic undertriggering (0 triggers across 5+ sessions where relevant tasks appeared), flag as "compounding risk" — undertriggered skills cannot self-improve through usage feedback, ca'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-optimizer/SKILL.md')
    assert '**This is the highest-value dimension.** For each skill, extract its **capability keywords** (not just trigger keywords — what the skill CAN do). Then scan user messages for tasks that match those cap' in text, "expected to find: " + '**This is the highest-value dimension.** For each skill, extract its **capability keywords** (not just trigger keywords — what the skill CAN do). Then scan user messages for tasks that match those cap'[:80]

