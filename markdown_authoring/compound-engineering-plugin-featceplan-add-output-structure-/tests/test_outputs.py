"""Behavioral checks for compound-engineering-plugin-featceplan-add-output-structure- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert 'The tree is a scope declaration showing the expected output shape. It is not a constraint — the implementer may adjust the structure if implementation reveals a better layout. The per-unit `**Files:**' in text, "expected to find: " + 'The tree is a scope declaration showing the expected output shape. It is not a constraint — the implementer may adjust the structure if implementation reveals a better layout. The per-unit `**Files:**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert 'For greenfield plans that create a new directory structure (new plugin, service, package, or module), include an `## Output Structure` section with a file tree showing the expected layout. This gives ' in text, "expected to find: " + 'For greenfield plans that create a new directory structure (new plugin, service, package, or module), include an `## Output Structure` section with a file tree showing the expected layout. This gives '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '- If Scope Boundaries lists items that are planned work for a separate PR or task, are they under `### Deferred to Separate Tasks` rather than mixed with true non-goals?' in text, "expected to find: " + '- If Scope Boundaries lists items that are planned work for a separate PR or task, are they under `### Deferred to Separate Tasks` rather than mixed with true non-goals?'[:80]

