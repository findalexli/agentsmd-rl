"""Behavioral checks for everything-claude-code-feat-add-hexagonal-architecture-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hexagonal-architecture/SKILL.md')
    assert 'Hexagonal architecture (Ports and Adapters) keeps business logic independent from frameworks, transport, and persistence details. The core app depends on abstract ports, and adapters implement those p' in text, "expected to find: " + 'Hexagonal architecture (Ports and Adapters) keeps business logic independent from frameworks, transport, and persistence details. The core app depends on abstract ports, and adapters implement those p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hexagonal-architecture/SKILL.md')
    assert 'description: Design, implement, and refactor Ports & Adapters systems with clear domain boundaries, dependency inversion, and testable use-case orchestration across TypeScript, Java, Kotlin, and Go se' in text, "expected to find: " + 'description: Design, implement, and refactor Ports & Adapters systems with clear domain boundaries, dependency inversion, and testable use-case orchestration across TypeScript, Java, Kotlin, and Go se'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hexagonal-architecture/SKILL.md')
    assert 'Outbound port interfaces usually live in the application layer (or in domain only when the abstraction is truly domain-level), while infrastructure adapters implement them.' in text, "expected to find: " + 'Outbound port interfaces usually live in the application layer (or in domain only when the abstraction is truly domain-level), while infrastructure adapters implement them.'[:80]

