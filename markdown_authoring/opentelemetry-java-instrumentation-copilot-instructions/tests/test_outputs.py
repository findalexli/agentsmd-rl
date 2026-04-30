"""Behavioral checks for opentelemetry-java-instrumentation-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentelemetry-java-instrumentation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'library that are not compatible with the instrumentation we disable the instrumentation instead of letting' in text, "expected to find: " + 'library that are not compatible with the instrumentation we disable the instrumentation instead of letting'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When registering tests in gradle configurations, if using `val testName by registering(Test::class) {`...' in text, "expected to find: " + 'When registering tests in gradle configurations, if using `val testName by registering(Test::class) {`...'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'In javaagent instrumentations we try not to break applications. If there are changes in the instrumented' in text, "expected to find: " + 'In javaagent instrumentations we try not to break applications. If there are changes in the instrumented'[:80]

