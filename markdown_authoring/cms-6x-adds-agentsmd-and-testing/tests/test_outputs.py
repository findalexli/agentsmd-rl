"""Behavioral checks for cms-6x-adds-agentsmd-and-testing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cms")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing-guidelines/SKILL.md')
    assert 'description: Guidance for writing and updating Craft CMS 6 tests (Pest/Laravel) including element factories, CP URL rules, custom field setup, trait testing, and event assertions. Use when creating or' in text, "expected to find: " + 'description: Guidance for writing and updating Craft CMS 6 tests (Pest/Laravel) including element factories, CP URL rules, custom field setup, trait testing, and event assertions. Use when creating or'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing-guidelines/SKILL.md')
    assert 'Apply Craft CMS 6 testing patterns consistently and avoid common pitfalls around elements, CP URLs, and event assertions. Use the quick rules below, then load the reference file for full examples and ' in text, "expected to find: " + 'Apply Craft CMS 6 testing patterns consistently and avoid common pitfalls around elements, CP URLs, and event assertions. Use the quick rules below, then load the reference file for full examples and '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing-guidelines/SKILL.md')
    assert '- Do not instantiate element classes directly with `new` in tests; use factories to ensure database state.' in text, "expected to find: " + '- Do not instantiate element classes directly with `new` in tests; use factories to ensure database state.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing-guidelines/references/testing-guidelines.md')
    assert 'When testing element traits/concerns, create a minimal test element class that extends `Element` and overrides only the methods you need to test:' in text, "expected to find: " + 'When testing element traits/concerns, create a minimal test element class that extends `Element` and overrides only the methods you need to test:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing-guidelines/references/testing-guidelines.md')
    assert 'This pattern allows testing trait behavior without needing factories or database state. See `tests/Element/Concerns/` for examples.' in text, "expected to find: " + 'This pattern allows testing trait behavior without needing factories or database state. See `tests/Element/Concerns/` for examples.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing-guidelines/references/testing-guidelines.md')
    assert 'Important: Do not instantiate element classes directly with `new Entry()` in tests. Use factories to ensure proper database state.' in text, "expected to find: " + 'Important: Do not instantiate element classes directly with `new Entry()` in tests. Use factories to ensure proper database state.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Classes marked `final` have this keyword stripped during testing** - you can create custom test classes that extend production classes (e.g., extending `User` element) to override methods like `ge' in text, "expected to find: " + '- **Classes marked `final` have this keyword stripped during testing** - you can create custom test classes that extend production classes (e.g., extending `User` element) to override methods like `ge'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- When writing tests, don't use Mockery or Mocks unless absolutely necessary. Prefer using Laravel's Facade fakes or running real code. Tests written are feature or integration tests and not unit test" in text, "expected to find: " + "- When writing tests, don't use Mockery or Mocks unless absolutely necessary. Prefer using Laravel's Facade fakes or running real code. Tests written are feature or integration tests and not unit test"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the Craft CMS 6.x repository. Craft CMS 6 is a major rewrite that migrates from Yii2 to Laravel 12 while maintaining backwards compatibility through a Yii2 adapter layer.' in text, "expected to find: " + 'This is the Craft CMS 6.x repository. Craft CMS 6 is a major rewrite that migrates from Yii2 to Laravel 12 while maintaining backwards compatibility through a Yii2 adapter layer.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

