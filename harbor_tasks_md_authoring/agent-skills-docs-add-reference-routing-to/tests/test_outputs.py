"""Behavioral checks for agent-skills-docs-add-reference-routing-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-review-and-quality/SKILL.md')
    assert '- For detailed security review guidance, see `references/security-checklist.md`' in text, "expected to find: " + '- For detailed security review guidance, see `references/security-checklist.md`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/code-review-and-quality/SKILL.md')
    assert '- For performance review checks, see `references/performance-checklist.md`' in text, "expected to find: " + '- For performance review checks, see `references/performance-checklist.md`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/frontend-ui-engineering/SKILL.md')
    assert 'For detailed accessibility requirements and testing tools, see `references/accessibility-checklist.md`.' in text, "expected to find: " + 'For detailed accessibility requirements and testing tools, see `references/accessibility-checklist.md`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performance-optimization/SKILL.md')
    assert 'For detailed performance checklists, optimization commands, and anti-pattern reference, see `references/performance-checklist.md`.' in text, "expected to find: " + 'For detailed performance checklists, optimization commands, and anti-pattern reference, see `references/performance-checklist.md`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/security-and-hardening/SKILL.md')
    assert 'For detailed security checklists and pre-commit verification steps, see `references/security-checklist.md`.' in text, "expected to find: " + 'For detailed security checklists and pre-commit verification steps, see `references/security-checklist.md`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shipping-and-launch/SKILL.md')
    assert '- For accessibility verification before launch, see `references/accessibility-checklist.md`' in text, "expected to find: " + '- For accessibility verification before launch, see `references/accessibility-checklist.md`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shipping-and-launch/SKILL.md')
    assert '- For performance pre-launch checklist, see `references/performance-checklist.md`' in text, "expected to find: " + '- For performance pre-launch checklist, see `references/performance-checklist.md`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shipping-and-launch/SKILL.md')
    assert '- For security pre-launch checks, see `references/security-checklist.md`' in text, "expected to find: " + '- For security pre-launch checks, see `references/security-checklist.md`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test-driven-development/SKILL.md')
    assert 'For detailed testing patterns, examples, and anti-patterns across frameworks, see `references/testing-patterns.md`.' in text, "expected to find: " + 'For detailed testing patterns, examples, and anti-patterns across frameworks, see `references/testing-patterns.md`.'[:80]

