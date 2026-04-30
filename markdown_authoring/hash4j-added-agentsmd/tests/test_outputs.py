"""Behavioral checks for hash4j-added-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hash4j")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Language**: Java (library/runtime baseline: Java 11; multi-release JAR support for Java 21 and 25; contributors typically build with the Gradle Java 25 toolchain and run tests for Java 11, 21, and' in text, "expected to find: " + '- **Language**: Java (library/runtime baseline: Java 11; multi-release JAR support for Java 21 and 25; contributors typically build with the Gradle Java 25 toolchain and run tests for Java 11, 21, and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'hash4j is a Java library by Dynatrace providing non-cryptographic hash algorithms and hash-based data structures. It is published to Maven Central as `com.dynatrace.hash4j:hash4j`.' in text, "expected to find: " + 'hash4j is a Java library by Dynatrace providing non-cryptographic hash algorithms and hash-based data structures. It is published to Maven Central as `com.dynatrace.hash4j:hash4j`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `hashing` — Hash algorithm implementations (Murmur3, Wyhash, Komihash, FarmHash, PolymurHash, XXHash, Rapidhash, ChibiHash, MetroHash)' in text, "expected to find: " + '- `hashing` — Hash algorithm implementations (Murmur3, Wyhash, Komihash, FarmHash, PolymurHash, XXHash, Rapidhash, ChibiHash, MetroHash)'[:80]

