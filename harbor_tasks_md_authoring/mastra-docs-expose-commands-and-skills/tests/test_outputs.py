"""Behavioral checks for mastra-docs-expose-commands-and-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mastra")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **E2E Tests for Studio** (`.claude/skills/e2e-tests-studio/SKILL.md`) — REQUIRED when modifying any file in `packages/playground-ui` or `packages/playground`. Covers Playwright E2E test generation t' in text, "expected to find: " + '- **E2E Tests for Studio** (`.claude/skills/e2e-tests-studio/SKILL.md`) — REQUIRED when modifying any file in `packages/playground-ui` or `packages/playground`. Covers Playwright E2E test generation t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **React Best Practices** (`.claude/skills/react-best-practices/SKILL.md`) — React performance optimization patterns. Read when writing, reviewing, or refactoring React components.' in text, "expected to find: " + '- **React Best Practices** (`.claude/skills/react-best-practices/SKILL.md`) — React performance optimization patterns. Read when writing, reviewing, or refactoring React components.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Tailwind Best Practices** (`.claude/skills/tailwind-best-practices/SKILL.md`) — Tailwind CSS and design-system guidelines for `packages/playground-ui` and `packages/playground`.' in text, "expected to find: " + '- **Tailwind Best Practices** (`.claude/skills/tailwind-best-practices/SKILL.md`) — Tailwind CSS and design-system guidelines for `packages/playground-ui` and `packages/playground`.'[:80]

