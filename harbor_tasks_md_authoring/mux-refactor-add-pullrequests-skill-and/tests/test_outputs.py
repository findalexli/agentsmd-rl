"""Behavioral checks for mux-refactor-add-pullrequests-skill-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mux")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.mux/skills/pull-requests/SKILL.md')
    assert 'When posting multi-line comments with `gh` (e.g., `@codex review`), **do not** rely on `\\n` escapes inside quoted `--body` strings (they will be sent as literal text). Prefer `--body-file -` with a he' in text, "expected to find: " + 'When posting multi-line comments with `gh` (e.g., `@codex review`), **do not** rely on `\\n` escapes inside quoted `--body` strings (they will be sent as literal text). Prefer `--body-file -` with a he'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.mux/skills/pull-requests/SKILL.md')
    assert 'Always check `$MUX_MODEL_STRING`, `$MUX_THINKING_LEVEL`, and `$MUX_COSTS_USD` via bash before creating or updating PRs—include them in the footer if set.' in text, "expected to find: " + 'Always check `$MUX_MODEL_STRING`, `$MUX_THINKING_LEVEL`, and `$MUX_COSTS_USD` via bash before creating or updating PRs—include them in the footer if set.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.mux/skills/pull-requests/SKILL.md')
    assert '- Waiting for PR checks can take 10+ minutes, so prefer local validation (e.g., run a subset of integration tests) to catch issues early.' in text, "expected to find: " + '- Waiting for PR checks can take 10+ minutes, so prefer local validation (e.g., run a subset of integration tests) to catch issues early.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- For PRs, commits, and public issues, consult the `pull-requests` skill for attribution footer requirements and workflow conventions.' in text, "expected to find: " + '- For PRs, commits, and public issues, consult the `pull-requests` skill for attribution footer requirements and workflow conventions.'[:80]

