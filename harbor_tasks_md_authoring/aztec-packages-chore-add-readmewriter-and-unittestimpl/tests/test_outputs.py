"""Behavioral checks for aztec-packages-chore-add-readmewriter-and-unittestimpl (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aztec-packages")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/readme-writer/SKILL.md')
    assert 'description: Guidelines for writing module READMEs that explain how a module works to developers who need to use it or understand its internals. Use when documenting a module, package, or subsystem.' in text, "expected to find: " + 'description: Guidelines for writing module READMEs that explain how a module works to developers who need to use it or understand its internals. Use when documenting a module, package, or subsystem.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/readme-writer/SKILL.md')
    assert 'Define domain-specific terms and objects (blocks, checkpoints, slots, proposals, offenses, etc.). Explain relationships between them.' in text, "expected to find: " + 'Define domain-specific terms and objects (blocks, checkpoints, slots, proposals, offenses, etc.). Explain relationships between them.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/readme-writer/SKILL.md')
    assert 'Use package-level READMEs when the package is small or you want to explain the package as a whole.' in text, "expected to find: " + 'Use package-level READMEs when the package is small or you want to explain the package as a whole.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/unit-test-implementation/SKILL.md')
    assert 'description: Best practices for implementing unit tests in this TypeScript monorepo. Use when writing new tests, refactoring existing tests, or fixing failing tests. Covers mocking strategies, test or' in text, "expected to find: " + 'description: Best practices for implementing unit tests in this TypeScript monorepo. Use when writing new tests, refactoring existing tests, or fixing failing tests. Covers mocking strategies, test or'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/unit-test-implementation/SKILL.md')
    assert '**Note:** This requires the base class to use `protected` (not `private`) for members you need to access. Feel free to modify the base class for this when writing its unit tests.' in text, "expected to find: " + '**Note:** This requires the base class to use `protected` (not `private`) for members you need to access. Feel free to modify the base class for this when writing its unit tests.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/unit-test-implementation/SKILL.md')
    assert "**When in doubt, ask the user** which dependencies should be mocked and which should use real instances. The decision depends on what behavior you're trying to test." in text, "expected to find: " + "**When in doubt, ask the user** which dependencies should be mocked and which should use real instances. The decision depends on what behavior you're trying to test."[:80]

