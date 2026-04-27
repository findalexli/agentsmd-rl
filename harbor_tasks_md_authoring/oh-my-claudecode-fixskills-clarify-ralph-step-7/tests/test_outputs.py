"""Behavioral checks for oh-my-claudecode-fixskills-clarify-ralph-step-7 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oh-my-claudecode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ralph/SKILL.md')
    assert '- **Skill vs agent invocation**: `ai-slop-cleaner` is a skill, invoke via `Skill("ai-slop-cleaner")`. `architect`, `critic`, `executor` etc. are agents, invoke via `Task(subagent_type="oh-my-claudecod' in text, "expected to find: " + '- **Skill vs agent invocation**: `ai-slop-cleaner` is a skill, invoke via `Skill("ai-slop-cleaner")`. `architect`, `critic`, `executor` etc. are agents, invoke via `Task(subagent_type="oh-my-claudecod'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ralph/SKILL.md')
    assert '- **Do NOT stop after Step 7 approval.** The boulder continues through 7 → 7.5 → 7.6 → 8 in the same turn as a single chain. Step 7 is a checkpoint inside the loop, not a reporting moment. Treating an' in text, "expected to find: " + '- **Do NOT stop after Step 7 approval.** The boulder continues through 7 → 7.5 → 7.6 → 8 in the same turn as a single chain. Step 7 is a checkpoint inside the loop, not a reporting moment. Treating an'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ralph/SKILL.md')
    assert '- **ai-slop-cleaner is a SKILL, not an agent.** Do NOT call it via `Task(subagent_type="oh-my-claudecode:ai-slop-cleaner")` — that subagent type does not exist and the call will fail with "Agent type ' in text, "expected to find: " + '- **ai-slop-cleaner is a SKILL, not an agent.** Do NOT call it via `Task(subagent_type="oh-my-claudecode:ai-slop-cleaner")` — that subagent type does not exist and the call will fail with "Agent type '[:80]

