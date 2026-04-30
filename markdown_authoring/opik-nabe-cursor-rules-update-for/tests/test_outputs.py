"""Behavioral checks for opik-nabe-cursor-rules-update-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opik")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_style.mdc')
    assert '**Rule**: Always use existing utility classes and helper methods instead of re-implementing common patterns. This ensures consistency, reduces duplication, and leverages properly configured shared ins' in text, "expected to find: " + '**Rule**: Always use existing utility classes and helper methods instead of re-implementing common patterns. This ensures consistency, reduces duplication, and leverages properly configured shared ins'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_style.mdc')
    assert '- **Tests**: Creating `new ObjectMapper()` in test classes is acceptable when testing serialization/deserialization behavior' in text, "expected to find: " + '- **Tests**: Creating `new ObjectMapper()` in test classes is acceptable when testing serialization/deserialization behavior'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_style.mdc')
    assert '- **Infrastructure classes**: Classes like `JsonNodeArgumentFactory` that need isolated instances for specific use cases' in text, "expected to find: " + '- **Infrastructure classes**: Classes like `JsonNodeArgumentFactory` that need isolated instances for specific use cases'[:80]

