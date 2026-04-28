"""Behavioral checks for uportal-docsagents-align-agentsmd-to-java (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uportal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Source compiles under Java 11, so Java 9–11 language features and APIs (`var`, `List.of()`, `Map.of()`, `Optional.isEmpty()`, `String.isBlank()`, etc.) are all fair game. The ban line is **Java 12 and' in text, "expected to find: " + 'Source compiles under Java 11, so Java 9–11 language features and APIs (`var`, `List.of()`, `Map.of()`, `Optional.isEmpty()`, `String.isBlank()`, etc.) are all fair game. The ban line is **Java 12 and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- 🚫 **Never do:** Guess at requirements. Add features that weren\'t asked for. "Improve" code adjacent to your change. Use Java 12+ features or APIs. Commit secrets.' in text, "expected to find: " + '- 🚫 **Never do:** Guess at requirements. Add features that weren\'t asked for. "Improve" code adjacent to your change. Use Java 12+ features or APIs. Commit secrets.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This project uses [SDKMAN](https://sdkman.io/) to manage Java versions. uPortal and uPortal-start both require **Java 11**. Common commands:' in text, "expected to find: " + 'This project uses [SDKMAN](https://sdkman.io/) to manage Java versions. uPortal and uPortal-start both require **Java 11**. Common commands:'[:80]

