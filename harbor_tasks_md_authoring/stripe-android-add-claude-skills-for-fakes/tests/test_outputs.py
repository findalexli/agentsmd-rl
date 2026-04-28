"""Behavioral checks for stripe-android-add-claude-skills-for-fakes (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stripe-android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-fake/SKILL.md')
    assert 'This skill describes how to create fake implementations for testing in the Stripe Android SDK. The codebase **strongly prefers fakes over mocks** for better test reliability and clarity.' in text, "expected to find: " + 'This skill describes how to create fake implementations for testing in the Stripe Android SDK. The codebase **strongly prefers fakes over mocks** for better test reliability and clarity.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-fake/SKILL.md')
    assert '1. **Prefer fakes over mocks** - Create `FakeClassName` implementations that provide controllable, inspectable behavior' in text, "expected to find: " + '1. **Prefer fakes over mocks** - Create `FakeClassName` implementations that provide controllable, inspectable behavior'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-fake/SKILL.md')
    assert '`paymentsheet/src/test/java/com/stripe/android/paymentsheet/verticalmode/FakePaymentMethodVerticalLayoutInteractor.kt`' in text, "expected to find: " + '`paymentsheet/src/test/java/com/stripe/android/paymentsheet/verticalmode/FakePaymentMethodVerticalLayoutInteractor.kt`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-tests/SKILL.md')
    assert 'This skill describes how to structure tests in the Stripe Android SDK using fakes, scenarios, and proper verification patterns.' in text, "expected to find: " + 'This skill describes how to structure tests in the Stripe Android SDK using fakes, scenarios, and proper verification patterns.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-tests/SKILL.md')
    assert "description: Explains how to write tests and structure test classes following stripe-android's coding standards" in text, "expected to find: " + "description: Explains how to write tests and structure test classes following stripe-android's coding standards"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-tests/SKILL.md')
    assert '3. **Verify all events consumed** - Call `validate()` or `ensureAllEventsConsumed()` on fakes after test block' in text, "expected to find: " + '3. **Verify all events consumed** - Call `validate()` or `ensureAllEventsConsumed()` on fakes after test block'[:80]

