"""Behavioral checks for contracts-tighten-cursor-rules-for-ts (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/contracts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/099-finish.mdc')
    assert '- **Linting**: Run the relevant linter on **all files you created or edited** (e.g. `bunx eslint` for TS/JS, or the project’s lint command) and fix all reported issues before finalizing. Do not claim ' in text, "expected to find: " + '- **Linting**: Run the relevant linter on **all files you created or edited** (e.g. `bunx eslint` for TS/JS, or the project’s lint command) and fix all reported issues before finalizing. Do not claim '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/099-finish.mdc')
    assert '**Scope**: This checklist applies to **every file you create or modify** during the task, including files you added or edited that were not mentioned in the user’s initial prompt. Before finalizing, r' in text, "expected to find: " + '**Scope**: This checklist applies to **every file you create or modify** during the task, including files you added or edited that were not mentioned in the user’s initial prompt. Before finalizing, r'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/200-typescript.mdc')
    assert '- When editing any file matching this rule’s globs, run `bunx eslint <file(s)>` and fix all reported issues before finalizing; do not introduce new lint violations.' in text, "expected to find: " + '- When editing any file matching this rule’s globs, run `bunx eslint <file(s)>` and fix all reported issues before finalizing; do not introduce new lint violations.'[:80]

