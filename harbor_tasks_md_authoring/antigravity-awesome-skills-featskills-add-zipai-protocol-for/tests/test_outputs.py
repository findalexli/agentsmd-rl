"""Behavioral checks for antigravity-awesome-skills-featskills-add-zipai-protocol-for (markdown_authoring task).

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
    text = _read('skills/zipai-optimizer/SKILL.md')
    assert '- **Context Overshadowing:** In extremely long sessions, aggressive anchor summarization might cause the agent to lose track of microscopic variable states dropped during context pruning.' in text, "expected to find: " + '- **Context Overshadowing:** In extremely long sessions, aggressive anchor summarization might cause the agent to lose track of microscopic variable states dropped during context pruning.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/zipai-optimizer/SKILL.md')
    assert '- **Ideation Constrained:** Do not use this protocol during pure creative brainstorming or open-ended design phases where exhaustive exploration and maximum token verbosity are required.' in text, "expected to find: " + '- **Ideation Constrained:** Do not use this protocol during pure creative brainstorming or open-ended design phases where exhaustive exploration and maximum token verbosity are required.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/zipai-optimizer/SKILL.md')
    assert '- **Log Blindness Risk:** Intelligent truncation via `grep` and `tail` may occasionally hide underlying root causes located outside the captured error boundaries.' in text, "expected to find: " + '- **Log Blindness Risk:** Intelligent truncation via `grep` and `tail` may occasionally hide underlying root causes located outside the captured error boundaries.'[:80]

