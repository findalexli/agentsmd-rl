"""Behavioral checks for kaset-chore-remove-github-copilot-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kaset")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/SKILL.md')
    assert '.github/skills/swift-concurrency/SKILL.md' in text, "expected to find: " + '.github/skills/swift-concurrency/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/actors.md')
    assert '.github/skills/swift-concurrency/references/actors.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/actors.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/async-await-basics.md')
    assert '.github/skills/swift-concurrency/references/async-await-basics.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/async-await-basics.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/async-sequences.md')
    assert '.github/skills/swift-concurrency/references/async-sequences.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/async-sequences.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/core-data.md')
    assert '.github/skills/swift-concurrency/references/core-data.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/core-data.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/glossary.md')
    assert '.github/skills/swift-concurrency/references/glossary.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/glossary.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/linting.md')
    assert '.github/skills/swift-concurrency/references/linting.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/linting.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/memory-management.md')
    assert '.github/skills/swift-concurrency/references/memory-management.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/memory-management.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/migration.md')
    assert '.github/skills/swift-concurrency/references/migration.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/migration.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/performance.md')
    assert '.github/skills/swift-concurrency/references/performance.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/performance.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/sendable.md')
    assert '.github/skills/swift-concurrency/references/sendable.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/sendable.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/tasks.md')
    assert '.github/skills/swift-concurrency/references/tasks.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/tasks.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/testing.md')
    assert '.github/skills/swift-concurrency/references/testing.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/testing.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swift-concurrency/references/threading.md')
    assert '.github/skills/swift-concurrency/references/threading.md' in text, "expected to find: " + '.github/skills/swift-concurrency/references/threading.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swiftui-liquid-glass/SKILL.md')
    assert '.github/skills/swiftui-liquid-glass/SKILL.md' in text, "expected to find: " + '.github/skills/swiftui-liquid-glass/SKILL.md'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swiftui-performance-audit/SKILL.md')
    assert '.github/skills/swiftui-performance-audit/SKILL.md' in text, "expected to find: " + '.github/skills/swiftui-performance-audit/SKILL.md'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swiftui-ui-patterns/SKILL.md')
    assert '.github/skills/swiftui-ui-patterns/SKILL.md' in text, "expected to find: " + '.github/skills/swiftui-ui-patterns/SKILL.md'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/swiftui-view-refactor/SKILL.md')
    assert '.github/skills/swiftui-view-refactor/SKILL.md' in text, "expected to find: " + '.github/skills/swiftui-view-refactor/SKILL.md'[:80]

