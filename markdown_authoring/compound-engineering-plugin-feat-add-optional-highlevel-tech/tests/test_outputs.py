"""Behavioral checks for compound-engineering-plugin-feat-add-optional-highlevel-tech (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-plan-beta/SKILL.md')
    assert '2. **Decisions, not code** - Capture approach, boundaries, files, dependencies, risks, and test scenarios. Do not pre-write implementation code or shell command choreography. Pseudo-code sketches or D' in text, "expected to find: " + '2. **Decisions, not code** - Capture approach, boundaries, files, dependencies, risks, and test scenarios. Do not pre-write implementation code or shell command choreography. Pseudo-code sketches or D'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan-beta/SKILL.md')
    assert '- Mermaid diagrams are encouraged when they clarify relationships or flows that prose alone would make hard to follow — ERDs for data model changes, sequence diagrams for multi-service interactions, s' in text, "expected to find: " + '- Mermaid diagrams are encouraged when they clarify relationships or flows that prose alone would make hard to follow — ERDs for data model changes, sequence diagrams for multi-service interactions, s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan-beta/SKILL.md')
    assert '- Pseudo-code sketches and DSL grammars are allowed in the High-Level Technical Design section and per-unit technical design fields when they communicate design direction. Frame them explicitly as dir' in text, "expected to find: " + '- Pseudo-code sketches and DSL grammars are allowed in the High-Level Technical Design section and per-unit technical design fields when they communicate design direction. Frame them explicitly as dir'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md')
    assert '- Add implementation code — no imports, exact method signatures, or framework-specific syntax. Pseudo-code sketches and DSL grammars are allowed in both the top-level High-Level Technical Design secti' in text, "expected to find: " + '- Add implementation code — no imports, exact method signatures, or framework-specific syntax. Pseudo-code sketches and DSL grammars are allowed in both the top-level High-Level Technical Design secti'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md')
    assert '- Strengthen, replace, or add a High-Level Technical Design section when the work warrants it and the current representation is weak, uses the wrong medium, or is absent where it would help. Preserve ' in text, "expected to find: " + '- Strengthen, replace, or add a High-Level Technical Design section when the work warrants it and the current representation is weak, uses the wrong medium, or is absent where it would help. Preserve '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md')
    assert '- Add `compound-engineering:research:best-practices-researcher` when the technical design involves a DSL, API surface, or pattern that benefits from external validation' in text, "expected to find: " + '- Add `compound-engineering:research:best-practices-researcher` when the technical design involves a DSL, API surface, or pattern that benefits from external validation'[:80]

