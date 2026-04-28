"""Behavioral checks for stasharr-docsagents-add-agentsmd-and-remove (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stasharr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document is a quick, practical guide for agentic coding assistants working in this repository. It summarizes how the project is structured, where to make changes, how to validate them, and how to' in text, "expected to find: " + 'This document is a quick, practical guide for agentic coding assistants working in this repository. It summarizes how the project is structured, where to make changes, how to validate them, and how to'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For “nothing to do” cases, start a bulk op with no items and set `setInfo("No scenes available …")` then `complete()`; do not add dummy “success” items' in text, "expected to find: " + '- For “nothing to do” cases, start a bulk op with no items and set `setInfo("No scenes available …")` then `complete()`; do not add dummy “success” items'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Methods returned by `startBulkOperation`: `updateItem`, `addItems`, `removeItem`, `updateItemName(s)`, `setSkippedInfo`, `setInfo`, `complete`' in text, "expected to find: " + '- Methods returned by `startBulkOperation`: `updateItem`, `addItems`, `removeItem`, `updateItemName(s)`, `setSkippedInfo`, `setInfo`, `complete`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

