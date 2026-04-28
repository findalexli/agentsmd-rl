"""Behavioral checks for jazz-docs-enrich-agentsmd-with-detailed (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jazz")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/spec/SKILL.md')
    assert '1. **Scan for missing requirements** — Review the document for gaps such as missing edge cases, undefined behavior, unspecified error handling, unclear scope boundaries, missing performance constraint' in text, "expected to find: " + '1. **Scan for missing requirements** — Review the document for gaps such as missing edge cases, undefined behavior, unspecified error handling, unclear scope boundaries, missing performance constraint'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/spec/SKILL.md')
    assert '1. **Scan for missing requirements** — Check whether the design covers all stated requirements and user stories. Identify any requirements that were dropped, under-specified, or only partially address' in text, "expected to find: " + '1. **Scan for missing requirements** — Check whether the design covers all stated requirements and user stories. Identify any requirements that were dropped, under-specified, or only partially address'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/spec/SKILL.md')
    assert '2. **Identify ambiguities** — Flag any requirements that could be interpreted in multiple ways, have vague language (e.g., "fast", "simple", "flexible"), or lack concrete acceptance criteria.' in text, "expected to find: " + '2. **Identify ambiguities** — Flag any requirements that could be interpreted in multiple ways, have vague language (e.g., "fast", "simple", "flexible"), or lack concrete acceptance criteria.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Jazz is a distributed database framework for building local-first applications. It provides real-time collaboration, offline support, and end-to-end encryption through CRDTs (Conflict-free Replicated ' in text, "expected to find: " + 'Jazz is a distributed database framework for building local-first applications. It provides real-time collaboration, offline support, and end-to-end encryption through CRDTs (Conflict-free Replicated '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **CoValue**: Base collaborative value type — the core data abstraction. Variants: `CoMap` (key-value), `CoList` (ordered list), `CoStream` (append-only stream), `CoPlainText` (collaborative text), `' in text, "expected to find: " + '- **CoValue**: Base collaborative value type — the core data abstraction. Variants: `CoMap` (key-value), `CoList` (ordered list), `CoStream` (append-only stream), `CoPlainText` (collaborative text), `'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- All core packages are in a **fixed version group** via Changesets (cojson, jazz-tools, jazz-run, jazz-webhook, all storage/transport packages, and NAPI binary packages)' in text, "expected to find: " + '- All core packages are in a **fixed version group** via Changesets (cojson, jazz-tools, jazz-run, jazz-webhook, all storage/transport packages, and NAPI binary packages)'[:80]

