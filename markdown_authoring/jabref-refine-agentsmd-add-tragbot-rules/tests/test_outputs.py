"""Behavioral checks for jabref-refine-agentsmd-add-tragbot-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jabref")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- In case Java comments are added, they should match the code following. They should be a high-level summary or guidance of the following code (and not some random text or just re-stating the obvious)' in text, "expected to find: " + '- In case Java comments are added, they should match the code following. They should be a high-level summary or guidance of the following code (and not some random text or just re-stating the obvious)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- New public methods should not return `null`. They should make use of `java.util.Optional`. In case `null` really needs to be used, the [JSpecify](https://jspecify.dev/) annotations must be used.' in text, "expected to find: " + '- New public methods should not return `null`. They should make use of `java.util.Optional`. In case `null` really needs to be used, the [JSpecify](https://jspecify.dev/) annotations must be used.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use modern Java best practices, such as Arguments.of() instead of new Object[] especially in JUnit tests or Path.of() instead of Paths.get(), to improve readability and maintainability.' in text, "expected to find: " + '- Use modern Java best practices, such as Arguments.of() instead of new Object[] especially in JUnit tests or Path.of() instead of Paths.get(), to improve readability and maintainability.'[:80]

