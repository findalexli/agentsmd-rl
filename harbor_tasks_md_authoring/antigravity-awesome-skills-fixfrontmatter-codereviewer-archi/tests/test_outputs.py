"""Behavioral checks for antigravity-awesome-skills-fixfrontmatter-codereviewer-archi (markdown_authoring task).

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
    text = _read('skills/architect-review/SKILL.md')
    assert 'description: Master software architect specializing in modern architecture' in text, "expected to find: " + 'description: Master software architect specializing in modern architecture'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/c-pro/SKILL.md')
    assert 'description: Write efficient C code with proper memory management, pointer' in text, "expected to find: " + 'description: Write efficient C code with proper memory management, pointer'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-reviewer/SKILL.md')
    assert 'description: Elite code review expert specializing in modern AI-powered code' in text, "expected to find: " + 'description: Elite code review expert specializing in modern AI-powered code'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/design-orchestration/SKILL.md')
    assert 'description:' in text, "expected to find: " + 'description:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/haskell-pro/SKILL.md')
    assert 'description: Expert Haskell engineer specializing in advanced type systems, pure' in text, "expected to find: " + 'description: Expert Haskell engineer specializing in advanced type systems, pure'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/multi-agent-brainstorming/SKILL.md')
    assert 'description:' in text, "expected to find: " + 'description:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performance-engineer/SKILL.md')
    assert 'description: Expert performance engineer specializing in modern observability,' in text, "expected to find: " + 'description: Expert performance engineer specializing in modern observability,'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/search-specialist/SKILL.md')
    assert 'description: Expert web researcher using advanced search techniques and' in text, "expected to find: " + 'description: Expert web researcher using advanced search techniques and'[:80]

