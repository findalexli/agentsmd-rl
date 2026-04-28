"""Behavioral checks for neo-docsagentos-formalize-resumption-protocol-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'During continuous agent sessions, an agent can succumb to "interruption amnesia." If the human commander injects a diagnostic sub-question or testing request (e.g., "test this A2A message" or "run thi' in text, "expected to find: " + 'During continuous agent sessions, an agent can succumb to "interruption amnesia." If the human commander injects a diagnostic sub-question or testing request (e.g., "test this A2A message" or "run thi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If a user interrupts your ticket lifecycle for a diagnostic test, meta-request, or side-quest, you **MUST** explicitly resume the ticket lifecycle and check the PR Definition of Done immediately after' in text, "expected to find: " + 'If a user interrupts your ticket lifecycle for a diagnostic test, meta-request, or side-quest, you **MUST** explicitly resume the ticket lifecycle and check the PR Definition of Done immediately after'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## 8. The Resumption Protocol (Interruption Amnesia)' in text, "expected to find: " + '## 8. The Resumption Protocol (Interruption Amnesia)'[:80]

