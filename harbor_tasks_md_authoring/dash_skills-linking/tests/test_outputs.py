"""Behavioral checks for dash_skills-linking (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dash-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-best-practices/SKILL.md')
    assert '- **[`dart-modern-features`](../dart-modern-features/SKILL.md)**: For idiomatic' in text, "expected to find: " + '- **[`dart-modern-features`](../dart-modern-features/SKILL.md)**: For idiomatic'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-best-practices/SKILL.md')
    assert 'usage of modern Dart features like Pattern Matching (useful for deep JSON' in text, "expected to find: " + 'usage of modern Dart features like Pattern Matching (useful for deep JSON'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-best-practices/SKILL.md')
    assert 'extraction), Records, and Switch Expressions.' in text, "expected to find: " + 'extraction), Records, and Switch Expressions.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-checks-migration/SKILL.md')
    assert '- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:' in text, "expected to find: " + '- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-checks-migration/SKILL.md')
    assert 'Best practices for the traditional `package:matcher` that is being migrated' in text, "expected to find: " + 'Best practices for the traditional `package:matcher` that is being migrated'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-checks-migration/SKILL.md')
    assert '- **[`dart-test-fundamentals`](../dart-test-fundamentals/SKILL.md)**: Core' in text, "expected to find: " + '- **[`dart-test-fundamentals`](../dart-test-fundamentals/SKILL.md)**: Core'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-matcher-best-practices/SKILL.md')
    assert '- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this' in text, "expected to find: " + '- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-matcher-best-practices/SKILL.md')
    assert '- **[`dart-test-fundamentals`](../dart-test-fundamentals/SKILL.md)**: Core' in text, "expected to find: " + '- **[`dart-test-fundamentals`](../dart-test-fundamentals/SKILL.md)**: Core'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-matcher-best-practices/SKILL.md')
    assert 'skill if you are migrating tests from `package:matcher` to modern' in text, "expected to find: " + 'skill if you are migrating tests from `package:matcher` to modern'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-modern-features/SKILL.md')
    assert '- **[`dart-best-practices`](../dart-best-practices/SKILL.md)**: General code' in text, "expected to find: " + '- **[`dart-best-practices`](../dart-best-practices/SKILL.md)**: General code'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-modern-features/SKILL.md')
    assert 'style and foundational Dart idioms that predate or complement the modern' in text, "expected to find: " + 'style and foundational Dart idioms that predate or complement the modern'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-modern-features/SKILL.md')
    assert '## Related Skills' in text, "expected to find: " + '## Related Skills'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-test-fundamentals/SKILL.md')
    assert '- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:' in text, "expected to find: " + '- **[`dart-matcher-best-practices`](../dart-matcher-best-practices/SKILL.md)**:'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-test-fundamentals/SKILL.md')
    assert '- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this' in text, "expected to find: " + '- **[`dart-checks-migration`](../dart-checks-migration/SKILL.md)**: Use this'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-test-fundamentals/SKILL.md')
    assert 'if the project is migrating to the modern `package:checks` (`check` calls).' in text, "expected to find: " + 'if the project is migrating to the modern `package:checks` (`check` calls).'[:80]

