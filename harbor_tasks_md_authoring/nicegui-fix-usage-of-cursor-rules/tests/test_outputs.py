"""Behavioral checks for nicegui-fix-usage-of-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nicegui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general.mdc')
    assert '2. [AGENTS.md](../../AGENTS.md) - AI agent guidelines and code review instructions' in text, "expected to find: " + '2. [AGENTS.md](../../AGENTS.md) - AI agent guidelines and code review instructions'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general.mdc')
    assert '3. [CONTRIBUTING.md](../../CONTRIBUTING.md) - Coding standards and workflow' in text, "expected to find: " + '3. [CONTRIBUTING.md](../../CONTRIBUTING.md) - Coding standards and workflow'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general.mdc')
    assert '1. [README.md](../../README.md) - Project overview and setup' in text, "expected to find: " + '1. [README.md](../../README.md) - Project overview and setup'[:80]

