"""Behavioral checks for kotlin-sdk-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kotlin-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Explicit API mode** is strict: all public APIs must have explicit visibility modifiers and return types.' in text, "expected to find: " + '- **Explicit API mode** is strict: all public APIs must have explicit visibility modifiers and return types.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- All tests for each module are located in `src/commonTest/kotlin/io/modelcontextprotocol/kotlin/sdk/`' in text, "expected to find: " + '- All tests for each module are located in `src/commonTest/kotlin/io/modelcontextprotocol/kotlin/sdk/`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Follow [Kotlin Coding Conventions](https://kotlinlang.org/docs/reference/coding-conventions.html).' in text, "expected to find: " + '- Follow [Kotlin Coding Conventions](https://kotlinlang.org/docs/reference/coding-conventions.html).'[:80]

