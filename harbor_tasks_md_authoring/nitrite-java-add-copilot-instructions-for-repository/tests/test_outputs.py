"""Behavioral checks for nitrite-java-add-copilot-instructions-for-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nitrite-java")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Nitrite Database is an open source embedded NoSQL database for Java. It's a multi-module Maven project that supports both in-memory and file-based persistent storage." in text, "expected to find: " + "Nitrite Database is an open source embedded NoSQL database for Java. It's a multi-module Maven project that supports both in-memory and file-based persistent storage."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When modifying storage adapters (`nitrite-mvstore-adapter`, `nitrite-rocksdb-adapter`), ensure compatibility with the core module' in text, "expected to find: " + '- When modifying storage adapters (`nitrite-mvstore-adapter`, `nitrite-rocksdb-adapter`), ensure compatibility with the core module'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Minimum compatibility:** Code must compile and run on Java 11 (as per maven.compiler.source=11 in pom.xml)' in text, "expected to find: " + '1. **Minimum compatibility:** Code must compile and run on Java 11 (as per maven.compiler.source=11 in pom.xml)'[:80]

