"""Behavioral checks for clinical_quality_language-add-claude-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/clinical-quality-language")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the **Clinical Quality Language (CQL)** reference implementation — an HL7 standard for expressing clinical knowledge used in Clinical Decision Support (CDS) and Clinical Quality Measurement (C' in text, "expected to find: " + 'This is the **Clinical Quality Language (CQL)** reference implementation — an HL7 standard for expressing clinical knowledge used in Clinical Decision Support (CDS) and Clinical Quality Measurement (C'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The codebase is **Kotlin/JVM** with some Java. Tests use **JUnit 5** with Hamcrest matchers. The `cql` and `elm` modules include Kotlin Multiplatform support (JS/WASM targets for the CQL playground at' in text, "expected to find: " + 'The codebase is **Kotlin/JVM** with some Java. Tests use **JUnit 5** with Hamcrest matchers. The `cql` and `elm` modules include Kotlin Multiplatform support (JS/WASM targets for the CQL playground at'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The primary source is under `Src/java/` and uses **Gradle** (Kotlin DSL) with a Gradle wrapper. All Gradle commands must be run from `Src/java/`.' in text, "expected to find: " + 'The primary source is under `Src/java/` and uses **Gradle** (Kotlin DSL) with a Gradle wrapper. All Gradle commands must be run from `Src/java/`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

