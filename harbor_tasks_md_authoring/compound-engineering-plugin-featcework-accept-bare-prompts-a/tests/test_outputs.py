"""Behavioral checks for compound-engineering-plugin-featcework-accept-bare-prompts-a (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '**Test Discovery** — Before implementing changes to a file, find its existing test files (search for test/spec files that import, reference, or share naming patterns with the implementation file). Whe' in text, "expected to find: " + '**Test Discovery** — Before implementing changes to a file, find its existing test files (search for test/spec files that import, reference, or share naming patterns with the implementation file). Whe'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '| **Large** | Cross-cutting, architectural decisions, 10+ files, touches auth/payments/migrations | Inform the user this would benefit from `/ce:brainstorm` or `/ce:plan` to surface edge cases and sco' in text, "expected to find: " + '| **Large** | Cross-cutting, architectural decisions, 10+ files, touches auth/payments/migrations | Inform the user this would benefit from `/ce:brainstorm` or `/ce:plan` to surface edge cases and sco'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert 'This command takes a work document (plan, specification, or todo file) or a bare prompt describing the work, and executes it systematically. The focus is on **shipping complete features** by understan' in text, "expected to find: " + 'This command takes a work document (plan, specification, or todo file) or a bare prompt describing the work, and executes it systematically. The focus is on **shipping complete features** by understan'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '**Test Discovery** — Before implementing changes to a file, find its existing test files (search for test/spec files that import, reference, or share naming patterns with the implementation file). Whe' in text, "expected to find: " + '**Test Discovery** — Before implementing changes to a file, find its existing test files (search for test/spec files that import, reference, or share naming patterns with the implementation file). Whe'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '| **Large** | Cross-cutting, architectural decisions, 10+ files, touches auth/payments/migrations | Inform the user this would benefit from `/ce:brainstorm` or `/ce:plan` to surface edge cases and sco' in text, "expected to find: " + '| **Large** | Cross-cutting, architectural decisions, 10+ files, touches auth/payments/migrations | Inform the user this would benefit from `/ce:brainstorm` or `/ce:plan` to surface edge cases and sco'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert 'This command takes a work document (plan, specification, or todo file) or a bare prompt describing the work, and executes it systematically. The focus is on **shipping complete features** by understan' in text, "expected to find: " + 'This command takes a work document (plan, specification, or todo file) or a bare prompt describing the work, and executes it systematically. The focus is on **shipping complete features** by understan'[:80]

