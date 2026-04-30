"""Behavioral checks for stagehand-update-cursorrules-and-claudemd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stagehand")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'This is a project that uses Stagehand V3, a browser automation framework with AI-powered `act`, `extract`, `observe`, and `agent` methods.' in text, "expected to find: " + 'This is a project that uses Stagehand V3, a browser automation framework with AI-powered `act`, `extract`, `observe`, and `agent` methods.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- `page`: Individual page objects accessed via `stagehand.context.pages()[i]` or created with `stagehand.context.newPage()`' in text, "expected to find: " + '- `page`: Individual page objects accessed via `stagehand.context.pages()[i]` or created with `stagehand.context.newPage()`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'Extract data from pages using natural language instructions. The `extract` method is called on the `stagehand` instance.' in text, "expected to find: " + 'Extract data from pages using natural language instructions. The `extract` method is called on the `stagehand` instance.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'This is a project that uses Stagehand V3, a browser automation framework with AI-powered `act`, `extract`, `observe`, and `agent` methods.' in text, "expected to find: " + 'This is a project that uses Stagehand V3, a browser automation framework with AI-powered `act`, `extract`, `observe`, and `agent` methods.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert '- `page`: Individual page objects accessed via `stagehand.context.pages()[i]` or created with `stagehand.context.newPage()`' in text, "expected to find: " + '- `page`: Individual page objects accessed via `stagehand.context.pages()[i]` or created with `stagehand.context.newPage()`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'Extract data from pages using natural language instructions. The `extract` method is called on the `stagehand` instance.' in text, "expected to find: " + 'Extract data from pages using natural language instructions. The `extract` method is called on the `stagehand` instance.'[:80]

