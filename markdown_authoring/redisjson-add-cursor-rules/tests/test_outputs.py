"""Behavioral checks for redisjson-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/redisjson")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rust.mdc')
    assert 'Start with `Vec` for sequences and `HashMap` for maps. They are highly optimized and cover most use cases. Only switch to other collections (`VecDeque`, `BTreeMap`, `LinkedList`, etc.) when profiling ' in text, "expected to find: " + 'Start with `Vec` for sequences and `HashMap` for maps. They are highly optimized and cover most use cases. Only switch to other collections (`VecDeque`, `BTreeMap`, `LinkedList`, etc.) when profiling '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rust.mdc')
    assert 'When designing enums that represent explicit choices, do NOT add an `Auto` or `Default` variant. Instead, use `Option<EnumType>` in APIs where the value might not be specified. This makes the API expl' in text, "expected to find: " + 'When designing enums that represent explicit choices, do NOT add an `Auto` or `Default` variant. Instead, use `Option<EnumType>` in APIs where the value might not be specified. This makes the API expl'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rust.mdc')
    assert 'Always implement `From` or `TryFrom` traits for type conversions instead of custom methods like `from_*()`, `to_*()`, or `into_*()`. This enables idiomatic usage with `.into()`, `?` operator, and gene' in text, "expected to find: " + 'Always implement `From` or `TryFrom` traits for type conversions instead of custom methods like `from_*()`, `to_*()`, or `into_*()`. This enables idiomatic usage with `.into()`, `?` operator, and gene'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'Each test should focus on verifying one specific behavior. Multiple related assertions are fine, but avoid testing unrelated behaviors in a single test.' in text, "expected to find: " + 'Each test should focus on verifying one specific behavior. Multiple related assertions are fine, but avoid testing unrelated behaviors in a single test.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'Flow tests are located in `tests/pytest/` and test the Redis module end-to-end through the Redis protocol.' in text, "expected to find: " + 'Flow tests are located in `tests/pytest/` and test the Redis module end-to-end through the Redis protocol.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert 'Test function names should describe what is being tested and the expected behavior.' in text, "expected to find: " + 'Test function names should describe what is being tested and the expected behavior.'[:80]

