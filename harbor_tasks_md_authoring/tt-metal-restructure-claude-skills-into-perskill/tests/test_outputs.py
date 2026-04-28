"""Behavioral checks for tt-metal-restructure-claude-skills-into-perskill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tt-metal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/CLAUDE.md')
    assert '**MANDATORY**: Before dispatching agents or taking action for the triggers below, you MUST first invoke the corresponding skill (or `Read` its `SKILL.md`) and follow the instructions inside it. Never ' in text, "expected to find: " + '**MANDATORY**: Before dispatching agents or taking action for the triggers below, you MUST first invoke the corresponding skill (or `Read` its `SKILL.md`) and follow the instructions inside it. Never '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/CLAUDE.md')
    assert '**Note:** Skills live in `.claude/skills/<name>/SKILL.md` relative to this file. Claude Code auto-discovers them when launched from inside `tt-llk/` (nested-subdirectory discovery). If the `Skill` too' in text, "expected to find: " + '**Note:** Skills live in `.claude/skills/<name>/SKILL.md` relative to this file. Claude Code auto-discovers them when launched from inside `tt-llk/` (nested-subdirectory discovery). If the `Skill` too'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/CLAUDE.md')
    assert '| Architecture, instruction, or LLK questions | `arch-lookup` (`.claude/skills/arch-lookup/SKILL.md`) | Orchestrates sage agents in parallel, aggregates results |' in text, "expected to find: " + '| Architecture, instruction, or LLK questions | `arch-lookup` (`.claude/skills/arch-lookup/SKILL.md`) | Orchestrates sage agents in parallel, aggregates results |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md')
    assert 'tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md' in text, "expected to find: " + 'tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md')
    assert 'tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md' in text, "expected to find: " + 'tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md')
    assert 'tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md' in text, "expected to find: " + 'tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('tt_metal/tt-llk/.claude/skills/run-test/SKILL.md')
    assert 'tt_metal/tt-llk/.claude/skills/run-test/SKILL.md' in text, "expected to find: " + 'tt_metal/tt-llk/.claude/skills/run-test/SKILL.md'[:80]

