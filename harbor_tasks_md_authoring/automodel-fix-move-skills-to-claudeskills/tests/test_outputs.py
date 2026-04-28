"""Behavioral checks for automodel-fix-move-skills-to-claudeskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/automodel")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/developer-guide/SKILL.md')
    assert '.claude/skills/developer-guide/SKILL.md' in text, "expected to find: " + '.claude/skills/developer-guide/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/distributed-training/SKILL.md')
    assert '.claude/skills/distributed-training/SKILL.md' in text, "expected to find: " + '.claude/skills/distributed-training/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/launcher-config/SKILL.md')
    assert '.claude/skills/launcher-config/SKILL.md' in text, "expected to find: " + '.claude/skills/launcher-config/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/model-onboarding/SKILL.md')
    assert 'from nemo_automodel.components.models.<name>.layers import <Name>Attention as NeMoAttention' in text, "expected to find: " + 'from nemo_automodel.components.models.<name>.layers import <Name>Attention as NeMoAttention'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/model-onboarding/SKILL.md')
    assert '- [ ] Ran parity-testing skill (state-dict round-trip, component parity, E2E forward pass)' in text, "expected to find: " + '- [ ] Ran parity-testing skill (state-dict round-trip, component parity, E2E forward pass)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/model-onboarding/SKILL.md')
    assert '- [ ] Created layer equivalence tests for every rewritten layer (matching model dtype)' in text, "expected to find: " + '- [ ] Created layer equivalence tests for every rewritten layer (matching model dtype)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/model-onboarding/llm-patterns.md')
    assert '.claude/skills/model-onboarding/llm-patterns.md' in text, "expected to find: " + '.claude/skills/model-onboarding/llm-patterns.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/model-onboarding/moe-patterns.md')
    assert '.claude/skills/model-onboarding/moe-patterns.md' in text, "expected to find: " + '.claude/skills/model-onboarding/moe-patterns.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/model-onboarding/vlm-patterns.md')
    assert '.claude/skills/model-onboarding/vlm-patterns.md' in text, "expected to find: " + '.claude/skills/model-onboarding/vlm-patterns.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/parity-testing/SKILL.md')
    assert '.claude/skills/parity-testing/SKILL.md' in text, "expected to find: " + '.claude/skills/parity-testing/SKILL.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/parity-testing/pitfalls.md')
    assert '.claude/skills/parity-testing/pitfalls.md' in text, "expected to find: " + '.claude/skills/parity-testing/pitfalls.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recipe-development/SKILL.md')
    assert '.claude/skills/recipe-development/SKILL.md' in text, "expected to find: " + '.claude/skills/recipe-development/SKILL.md'[:80]

