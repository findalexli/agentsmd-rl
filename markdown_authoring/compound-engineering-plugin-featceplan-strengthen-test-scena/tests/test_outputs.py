"""Behavioral checks for compound-engineering-plugin-featceplan-strengthen-test-scena (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert 'When modifying a skill that has a `-beta` counterpart (or vice versa), always check the other version and **state your sync decision explicitly** before committing — e.g., "Propagated to beta — shared' in text, "expected to find: " + 'When modifying a skill that has a `-beta` counterpart (or vice versa), always check the other version and **state your sync decision explicitly** before committing — e.g., "Propagated to beta — shared'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert '### Stable/Beta Sync' in text, "expected to find: " + '### Stable/Beta Sync'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert "- **Test scenarios** - enumerate the specific test cases the implementer should write, right-sized to the unit's complexity and risk. Consider each category below and include scenarios from every cate" in text, "expected to find: " + "- **Test scenarios** - enumerate the specific test cases the implementer should write, right-sized to the unit's complexity and risk. Consider each category below and include scenarios from every cate"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert "- Test scenarios are vague (don't name inputs and expected outcomes), skip applicable categories (e.g., no error paths for a unit with failure modes, no integration scenarios for a unit crossing layer" in text, "expected to find: " + "- Test scenarios are vague (don't name inputs and expected outcomes), skip applicable categories (e.g., no error paths for a unit with failure modes, no integration scenarios for a unit crossing layer"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '- **Integration scenarios** (when the unit crosses layers) - behaviors that mocks alone will not prove, e.g., "creating X triggers callback Y which persists Z". Include these for any unit touching cal' in text, "expected to find: " + '- **Integration scenarios** (when the unit crosses layers) - behaviors that mocks alone will not prove, e.g., "creating X triggers callback Y which persists Z". Include these for any unit touching cal'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert "**Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or sc" in text, "expected to find: " + "**Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or sc"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '| **Error/failure paths** | When the unit has failure modes (validation, external calls, permissions) | Enumerate invalid inputs the unit should reject, permission/auth denials it should enforce, and ' in text, "expected to find: " + '| **Error/failure paths** | When the unit has failure modes (validation, external calls, permissions) | Enumerate invalid inputs the unit should reject, permission/auth denials it should enforce, and '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert "- Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests" in text, "expected to find: " + "- Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert "**Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or sc" in text, "expected to find: " + "**Test Scenario Completeness** — Before writing tests for a feature-bearing unit, check whether the plan's `Test scenarios` cover all categories that apply to this unit. If a category is missing or sc"[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '| **Error/failure paths** | When the unit has failure modes (validation, external calls, permissions) | Enumerate invalid inputs the unit should reject, permission/auth denials it should enforce, and ' in text, "expected to find: " + '| **Error/failure paths** | When the unit has failure modes (validation, external calls, permissions) | Enumerate invalid inputs the unit should reject, permission/auth denials it should enforce, and '[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert "- Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests" in text, "expected to find: " + "- Instruction to check whether the unit's test scenarios cover all applicable categories (happy paths, edge cases, error paths, integration) and supplement gaps before writing tests"[:80]

