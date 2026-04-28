"""Behavioral checks for kleinanzeigen-bot-docs-introduce-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kleinanzeigen-bot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Prefer tracked repo files and CI as the source of truth. If this file conflicts with them, the tracked docs/workflows win. Make minimal, focused changes that match existing patterns.' in text, "expected to find: " + 'Prefer tracked repo files and CI as the source of truth. If this file conflicts with them, the tracked docs/workflows win. Make minimal, focused changes that match existing patterns.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Keep log message strings in plain English; do **not** wrap `LOG.*`/`logger.*` strings with `_()`, because logging messages are translated by `TranslatingLogger`.' in text, "expected to find: " + '- Keep log message strings in plain English; do **not** wrap `LOG.*`/`logger.*` strings with `_()`, because logging messages are translated by `TranslatingLogger`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'CI and workflows are the source of truth for the exact required checks, coverage gates, generated-artifact verification, and PR title validation.' in text, "expected to find: " + 'CI and workflows are the source of truth for the exact required checks, coverage gates, generated-artifact verification, and PR title validation.'[:80]

