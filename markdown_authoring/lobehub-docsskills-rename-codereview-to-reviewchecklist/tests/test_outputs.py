"""Behavioral checks for lobehub-docsskills-rename-codereview-to-reviewchecklist (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobehub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-checklist/SKILL.md')
    assert "description: 'Common recurring mistakes in LobeHub code review — console leftovers, missing return await, hardcoded secrets, hardcoded i18n strings, desktop router pair drift, antd vs @lobehub/ui, non" in text, "expected to find: " + "description: 'Common recurring mistakes in LobeHub code review — console leftovers, missing return await, hardcoded secrets, hardcoded i18n strings, desktop router pair drift, antd vs @lobehub/ui, non"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-checklist/SKILL.md')
    assert 'name: review-checklist' in text, "expected to find: " + 'name: review-checklist'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-checklist/SKILL.md')
    assert '# Review Checklist' in text, "expected to find: " + '# Review Checklist'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Before reviewing a PR / diff / branch change, read the **review-checklist** skill (`.agents/skills/review-checklist/SKILL.md`) — it lists the recurring mistakes specific to this codebase.' in text, "expected to find: " + 'Before reviewing a PR / diff / branch change, read the **review-checklist** skill (`.agents/skills/review-checklist/SKILL.md`) — it lists the recurring mistakes specific to this codebase.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `pnpm i18n` is slow; run it manually when locale keys need updating (e.g. before opening a PR).' in text, "expected to find: " + '- `pnpm i18n` is slow; run it manually when locale keys need updating (e.g. before opening a PR).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '### Code Review' in text, "expected to find: " + '### Code Review'[:80]

