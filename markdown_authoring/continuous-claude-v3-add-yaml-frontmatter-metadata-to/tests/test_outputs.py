"""Behavioral checks for continuous-claude-v3-add-yaml-frontmatter-metadata-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/continuous-claude-v3")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert 'name: commit' in text, "expected to find: " + 'name: commit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/continuity_ledger/SKILL.md')
    assert 'name: continuity-ledger' in text, "expected to find: " + 'name: continuity-ledger'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create_handoff/SKILL.md')
    assert 'name: create-handoff' in text, "expected to find: " + 'name: create-handoff'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug/SKILL.md')
    assert '.claude/skills/debug/SKILL.md' in text, "expected to find: " + '.claude/skills/debug/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/describe_pr/SKILL.md')
    assert 'name: describe-pr' in text, "expected to find: " + 'name: describe-pr'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/discovery-interview/SKILL.md')
    assert 'name: discovery-interview' in text, "expected to find: " + 'name: discovery-interview'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/loogle-search/SKILL.md')
    assert 'description: Search Mathlib for lemmas by type signature pattern' in text, "expected to find: " + 'description: Search Mathlib for lemmas by type signature pattern'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/loogle-search/SKILL.md')
    assert 'name: loogle-search' in text, "expected to find: " + 'name: loogle-search'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/plan-agent/SKILL.md')
    assert 'name: planning-agent' in text, "expected to find: " + 'name: planning-agent'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall/SKILL.md')
    assert 'description: Query the memory system for relevant learnings from past sessions' in text, "expected to find: " + 'description: Query the memory system for relevant learnings from past sessions'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall/SKILL.md')
    assert 'user-invocable: false' in text, "expected to find: " + 'user-invocable: false'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall/SKILL.md')
    assert 'name: recall' in text, "expected to find: " + 'name: recall'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/remember/SKILL.md')
    assert 'description: Store a learning, pattern, or decision in the memory system for future recall' in text, "expected to find: " + 'description: Store a learning, pattern, or decision in the memory system for future recall'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/remember/SKILL.md')
    assert 'user-invocable: false' in text, "expected to find: " + 'user-invocable: false'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/remember/SKILL.md')
    assert 'name: remember' in text, "expected to find: " + 'name: remember'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/repo-research-analyst/SKILL.md')
    assert 'name: repo-research-analyst' in text, "expected to find: " + 'name: repo-research-analyst'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resume_handoff/SKILL.md')
    assert 'name: resume-handoff' in text, "expected to find: " + 'name: resume-handoff'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/system_overview/SKILL.md')
    assert 'description: Show users how Continuous Claude works - the opinionated setup with hooks, memory, and coordination' in text, "expected to find: " + 'description: Show users how Continuous Claude works - the opinionated setup with hooks, memory, and coordination'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/system_overview/SKILL.md')
    assert 'name: system-overview' in text, "expected to find: " + 'name: system-overview'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-deep/SKILL.md')
    assert 'description: Full 5-layer analysis of a specific function. Use when debugging or deeply understanding code.' in text, "expected to find: " + 'description: Full 5-layer analysis of a specific function. Use when debugging or deeply understanding code.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-deep/SKILL.md')
    assert 'name: tldr-deep' in text, "expected to find: " + 'name: tldr-deep'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-overview/SKILL.md')
    assert 'description: Get a token-efficient overview of any project using the TLDR stack' in text, "expected to find: " + 'description: Get a token-efficient overview of any project using the TLDR stack'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-overview/SKILL.md')
    assert 'name: tldr-overview' in text, "expected to find: " + 'name: tldr-overview'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-router/SKILL.md')
    assert 'description: Maps questions to the optimal tldr command. Use this to pick the right layer' in text, "expected to find: " + 'description: Maps questions to the optimal tldr command. Use this to pick the right layer'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-router/SKILL.md')
    assert 'name: tldr-router' in text, "expected to find: " + 'name: tldr-router'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tldr-stats/SKILL.md')
    assert 'name: tldr-stats' in text, "expected to find: " + 'name: tldr-stats'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tour/SKILL.md')
    assert 'description: Friendly onboarding when users ask about capabilities' in text, "expected to find: " + 'description: Friendly onboarding when users ask about capabilities'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/validate-agent/SKILL.md')
    assert 'name: validate-agent' in text, "expected to find: " + 'name: validate-agent'[:80]

