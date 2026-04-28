"""Behavioral checks for detekt-clarify-prerequisites-in-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/detekt")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Android SDK must be installed to execute certain tests. They will be skipped if the SDK is not installed. This is only an issue if making changes to detekt-gradle-plugin.' in text, "expected to find: " + '- Android SDK must be installed to execute certain tests. They will be skipped if the SDK is not installed. This is only an issue if making changes to detekt-gradle-plugin.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Note that some detekt-gradle-plugin tests only run on JDK 19 or lower' in text, "expected to find: " + '- Note that some detekt-gradle-plugin tests only run on JDK 19 or lower'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- JDK 17 must be available for build-logic JVM toolchain' in text, "expected to find: " + '- JDK 17 must be available for build-logic JVM toolchain'[:80]

