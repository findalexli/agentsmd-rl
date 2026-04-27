"""Behavioral checks for goose-harden-code-review-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/goose")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code-review/SKILL.md')
    assert 'If the project has a stronger pre-push or CI gate than this helper set, run that fuller gate when the review is meant to be PR-ready, but only after confirming it is also non-mutating (or run it from ' in text, "expected to find: " + 'If the project has a stronger pre-push or CI gate than this helper set, run that fuller gate when the review is meant to be PR-ready, but only after confirming it is also non-mutating (or run it from '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code-review/SKILL.md')
    assert "Before reading any code, run the project's CI gate to establish a baseline. Use **check-only** commands so the baseline never mutates the working tree — otherwise auto-formatters can introduce unstage" in text, "expected to find: " + "Before reading any code, run the project's CI gate to establish a baseline. Use **check-only** commands so the baseline never mutates the working tree — otherwise auto-formatters can introduce unstage"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/code-review/SKILL.md')
    assert '- **Dependent State Invalidation**: When a parent selection changes (provider/project/persona/workspace/etc.), are dependent values like `modelId`, `modelName`, defaults, or cached labels cleared or r' in text, "expected to find: " + '- **Dependent State Invalidation**: When a parent selection changes (provider/project/persona/workspace/etc.), are dependent values like `modelId`, `modelName`, defaults, or cached labels cleared or r'[:80]

